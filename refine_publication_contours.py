import cv2
import numpy as np
import json
import sys
import os
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, '.')
import build_atlas_data as bad

PX_PER_UNIT = 600
OUT_PER_UNIT = 100
X_RANGE = (-1.45, 1.45)
Y_RANGE = (-3.40, 3.40)
WIDTH = int((X_RANGE[1] - X_RANGE[0]) * PX_PER_UNIT)   # 1740
HEIGHT = int((Y_RANGE[1] - Y_RANGE[0]) * PX_PER_UNIT) # 4080
SCALE = OUT_PER_UNIT / PX_PER_UNIT                     # 1/6

WORKSPACE_HAND_REFINED = 'hand_nano_refined.jpg' if os.path.exists('hand_nano_refined.jpg') else '../AQ-Tech/MuscleAtlas/hand_nano_refined.jpg'

print("Loading BodyParts3D 3.0 meshes from muscles.glb...")
meshes = bad.load_meshes()
u_front = np.zeros((HEIGHT, WIDTH), np.uint8)
for k, (v, f) in meshes.items():
    if k in ('tibialis-posterior', 'flexor-digitorum-longus'):
        continue
    u_front = cv2.bitwise_or(u_front, bad.rasterize(v, f, 'front'))
v1_front = bad.body_silhouette_v1(u_front)

def draw_tapered_capsule(mask, p0, p1, r0, r1, val=255):
    p0, p1 = np.array(p0, dtype=float), np.array(p1, dtype=float)
    for t in np.linspace(0.0, 1.0, 100):
        p = p0 * (1 - t) + p1 * t
        r = r0 * (1 - t) + r1 * t
        cv2.circle(mask, (int(round(p[0] * 16)), int(round(p[1] * 16))), int(round(r * 16)), val, -1, lineType=cv2.LINE_AA, shift=4)

def build_final_silhouette(base_mask):
    m = base_mask.copy()
    
    # 1. HANDS: 3D-aligned full-width base refined by Nanobanana (hand_nano_refined.jpg)
    refined_img = cv2.imread(WORKSPACE_HAND_REFINED)
    gray_ref = cv2.cvtColor(refined_img, cv2.COLOR_BGR2GRAY)
    mask_ref_1000 = (gray_ref < 250).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(mask_ref_1000, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_c = max(cnts, key=cv2.contourArea)
    filled_1000 = np.zeros_like(mask_ref_1000)
    cv2.drawContours(filled_1000, [main_c], -1, 255, -1)
    filled_1000 = cv2.erode(filled_1000, np.ones((3, 3), np.uint8), iterations=2)
    
    mask_ref_500 = cv2.resize(filled_1000, (500, 500), interpolation=cv2.INTER_AREA)
    mask_ref_500 = (mask_ref_500 > 127).astype(np.uint8) * 255
    
    m[2000:2450, 20:430] = 0
    m[2000:2450, 1736-430:1736-20] = 0
    
    for sy in range(50, 500):
        dy = 1950 + sy
        for sx in range(410):
            if mask_ref_500[sy, sx] > 0:
                dx = 20 + sx
                m[dy, dx] = 255
                dx_r = int(round(1736.0 - dx))
                if 0 <= dx_r < WIDTH:
                    m[dy, dx_r] = 255
                    
    hand_band = m[1985:2450, :].astype(np.float32)
    hand_band = cv2.GaussianBlur(hand_band, (9, 9), 2.0)
    m[1985:2450, :] = (hand_band > 127).astype(np.uint8) * 255

    # 2. FEET: pure additive medial arch & Hallux (D1) tangent to shin at y=3800 + smooth forefoot cascade
    for is_right in [False, True]:
        def tx_f(x):
            return (1739.0 - x) if is_right else x
        
        draw_tapered_capsule(m, (tx_f(722), 3800), (tx_f(730), 4005), 11.0, 20.0, 255) # Hallux (D1)
        draw_tapered_capsule(m, (tx_f(728), 4006), (tx_f(674), 4008), 20.0, 18.5, 255) # Hallux -> D2
        draw_tapered_capsule(m, (tx_f(674), 4008), (tx_f(618), 4004), 18.5, 16.0, 255) # D2 -> D3
        draw_tapered_capsule(m, (tx_f(618), 4004), (tx_f(554), 3997), 16.0, 15.0, 255) # D3 -> rounded D5

    foot_band = m[3660:4060, :].astype(np.float32)
    foot_band = cv2.GaussianBlur(foot_band, (21, 21), 4.5)
    m[3660:4060, :] = (foot_band > 127).astype(np.uint8) * 255
    return m

def vectorize_mask(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    main_c = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(main_c, 0.80, True)[:, 0, :].astype(float)
    
    diffs = np.diff(approx, axis=0, append=approx[:1])
    dists = np.hypot(diffs[:, 0], diffs[:, 1])
    total_len = dists.sum()
    n_samples = int(total_len / 2.6)
    cum_dists = np.concatenate([[0], np.cumsum(dists)])
    sample_dists = np.linspace(0, total_len, n_samples, endpoint=False)
    
    pts_x = np.interp(sample_dists, cum_dists, np.concatenate([approx[:, 0], [approx[0, 0]]]))
    pts_y = np.interp(sample_dists, cum_dists, np.concatenate([approx[:, 1], [approx[0, 1]]]))
    uniform_pts = np.column_stack([pts_x, pts_y])
    
    smoothed = gaussian_filter1d(uniform_pts, sigma=1.35, axis=0, mode='wrap')
    pts_svg = (smoothed * SCALE)[::2]
    
    n = len(pts_svg)
    d = [f"M{pts_svg[0][0]:.2f} {pts_svg[0][1]:.2f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts_svg[(i - 1) % n], pts_svg[i], pts_svg[(i + 1) % n], pts_svg[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        d.append(f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    return "".join(d) + "Z"

print("Building final silhouette...")
mask_front = build_final_silhouette(v1_front)
mask_back  = np.fliplr(mask_front)

data_file = 'muscle_map_data.json' if os.path.exists('muscle_map_data.json') else 'atlas_data.json'
with open(data_file, 'r', encoding='utf-8') as f:
    atlas = json.load(f)

atlas['views']['front']['body'] = vectorize_mask(mask_front)
atlas['views']['back']['body']  = vectorize_mask(mask_back)

for vk in ('front', 'back'):
    for old_k in list(atlas['views'][vk].keys()):
        if old_k not in ('bbox', 'crotch', 'body'):
            del atlas['views'][vk][old_k]

for m_entry in atlas['muscles']:
    if m_entry['id'] == 'extensor-digitorum-brevis':
        v1, f1 = meshes['extensor-digitorum-brevis']
        v2, f2 = meshes['extensor-hallucis-brevis']
        m_comb = cv2.bitwise_or(bad.rasterize(v1, f1, 'front'), bad.rasterize(v2, f2, 'front'))
        m_entry['views']['front']['d'] = bad.contour_path(bad.smooth_mask(m_comb, close=5, sigma=3.5))
    elif m_entry['id'] == 'extensor-digitorum-longus':
        v1, f1 = meshes['extensor-digitorum-longus']
        v2, f2 = meshes['extensor-hallucis-longus']
        m_comb = cv2.bitwise_or(bad.rasterize(v1, f1, 'front'), bad.rasterize(v2, f2, 'front'))
        m_entry['views']['front']['d'] = bad.contour_path(bad.smooth_mask(m_comb, close=5, sigma=3.5))
    elif m_entry['id'] in ('flexor-digitorum-superficialis', 'extensor-digitorum'):
        view_k = 'front' if m_entry['id'] == 'flexor-digitorum-superficialis' else 'back'
        v1, f1 = meshes[m_entry['id']]
        m_comb = bad.rasterize(v1, f1, view_k)
        for is_right in [False, True]:
            def tx_t(x):
                return (1736.0 - x) if is_right else x
            poly_t_clear = np.array([
                [int(tx_t(110)), 2280], [int(tx_t(355)), 2280],
                [int(tx_t(355)), 2420], [int(tx_t(110)), 2420]
            ], dtype=np.int32)
            cv2.fillPoly(m_comb, [poly_t_clear], 0)
            tendons = [
                ((tx_t(169), 2245), (tx_t(148), 2348), 3.4, 2.5),
                ((tx_t(218), 2245), (tx_t(203), 2374), 3.6, 2.6),
                ((tx_t(268), 2245), (tx_t(260), 2365), 3.4, 2.5),
                ((tx_t(314), 2240), (tx_t(322), 2330), 3.0, 2.2),
            ]
            for p0, p1, r0, r1 in tendons:
                draw_tapered_capsule(m_comb, p0, p1, r0, r1, 255)
        m_entry['views'][view_k]['d'] = bad.contour_path(bad.smooth_mask(m_comb, close=5, sigma=3.5))
    
    for vk in list(m_entry['views'].keys()):
        m_entry['views'][vk].pop('d_v1', None)

with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(atlas, f, ensure_ascii=False, separators=(',', ':'))

print(f"Contours et pieds lissés mis à jour dans {data_file} !")
