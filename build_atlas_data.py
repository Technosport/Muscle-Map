"""Projette les maillages BodyParts3D (face / dos) en tracés vectoriels lissés pour Muscle Map.

Sortie : muscle_map_data.json (contour du corps + un tracé par muscle et par vue).
Usage : python build_atlas_data.py
"""
import os
import json
from pathlib import Path
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter1d
import trimesh

GLB = "muscles.glb" if os.path.exists("muscles.glb") else "../AQ-Tech/MuscleStudio/muscles.glb"
OUT = "muscle_map_data.json"

PX_PER_UNIT = 600      # résolution de rasterisation
OUT_PER_UNIT = 100     # unités du viewBox SVG par unité du modèle
X_RANGE = (-1.45, 1.45)
Y_RANGE = (-3.40, 3.40)

# id -> (section, vues, nom FR, nom EN, abbr, layer, standardized_color)
LAYOUT = {
    # Tête et cou
    "frontalis": ("Tête et cou", ["front"], "Frontal", "Frontalis", "FRO", "superficial", "#6366F1"),
    "temporalis": ("Tête et cou", ["front"], "Temporal", "Temporalis", "TEMP", "intermediate", "#8B5CF6"),
    "masseter": ("Tête et cou", ["front"], "Masséter", "Masseter", "MASS", "intermediate", "#EC4899"),
    "orbicularis-oculi": ("Tête et cou", ["front"], "Orbiculaire de l’œil", "Orbicularis oculi", "OO", "superficial", "#3B82F6"),
    "orbicularis-oris": ("Tête et cou", ["front"], "Orbiculaire de la bouche", "Orbicularis oris", "OOR", "superficial", "#F43F5E"),
    "zygomaticus-major": ("Tête et cou", ["front"], "Grand zygomatique", "Zygomaticus major", "ZYG", "superficial", "#FB7185"),
    "platysma": ("Tête et cou", ["front"], "Platysma", "Platysma", "PLA", "superficial", "#A855F7"),
    "sternocleidomastoid": ("Tête et cou", ["front"], "Sterno-cléido-mastoïdien", "Sternocleidomastoid", "SCM", "superficial", "#06B6D4"),
    "splenius-capitis": ("Tête et cou", ["back"], "Splénius de la tête", "Splenius capitis", "SPL", "intermediate", "#64748B"),

    # Tronc
    "pectoralis-major": ("Tronc", ["front"], "Grand pectoral", "Pectoralis major", "PM", "superficial", "#E11D48"),
    "serratus-anterior": ("Tronc", ["front"], "Dentelé antérieur", "Serratus anterior", "SA", "intermediate", "#F97316"),
    "rectus-abdominis": ("Tronc", ["front"], "Grand droit de l’abdomen", "Rectus abdominis", "RA", "superficial", "#EF4444"),
    "external-oblique": ("Tronc", ["front"], "Oblique externe", "External oblique", "EO", "superficial", "#EA580C"),
    "internal-oblique": ("Tronc", ["front"], "Oblique interne", "Internal oblique", "IO", "intermediate", "#F59E0B"),
    "trapezius-upper": ("Tronc", ["back"], "Trapèze supérieur", "Upper trapezius", "UT", "superficial", "#0D9488"),
    "trapezius-middle": ("Tronc", ["back"], "Trapèze moyen", "Middle trapezius", "MT", "superficial", "#059669"),
    "trapezius-lower": ("Tronc", ["back"], "Trapèze inférieur", "Lower trapezius", "LT", "superficial", "#10B981"),
    "latissimus-dorsi": ("Tronc", ["back"], "Grand dorsal", "Latissimus dorsi", "LD", "superficial", "#1E40AF"),
    "rhomboid-major": ("Tronc", ["back"], "Rhomboïde majeur", "Rhomboid major", "RHOM", "intermediate", "#7E22CE"),
    "levator-scapulae": ("Tronc", ["back"], "Élévateur de la scapula", "Levator scapulae", "LS", "intermediate", "#0284C7"),
    "iliocostalis": ("Tronc", ["back"], "Ilio-costal", "Iliocostalis", "IL", "deep", "#475569"),
    "longissimus": ("Tronc", ["back"], "Longissimus", "Longissimus", "LONG", "deep", "#334155"),
    "multifidus": ("Tronc", ["back"], "Multifide", "Multifidus", "MULT", "deep", "#1E293B"),

    # Épaule et bras
    "deltoid-anterior": ("Épaule et bras", ["front"], "Deltoïde antérieur", "Anterior deltoid", "AD", "superficial", "#F97316"),
    "deltoid-middle": ("Épaule et bras", ["front", "back"], "Deltoïde moyen", "Middle deltoid", "MD", "superficial", "#FB923C"),
    "deltoid-posterior": ("Épaule et bras", ["back"], "Deltoïde postérieur", "Posterior deltoid", "PD", "superficial", "#EA580C"),
    "biceps-brachii-long": ("Épaule et bras", ["front"], "Biceps brachial (chef long)", "Biceps brachii (long head)", "BBL", "superficial", "#2563EB"),
    "biceps-brachii-short": ("Épaule et bras", ["front"], "Biceps brachial (chef court)", "Biceps brachii (short head)", "BBS", "superficial", "#3B82F6"),
    "infraspinatus": ("Épaule et bras", ["back"], "Infra-épineux", "Infraspinatus", "INF", "intermediate", "#9333EA"),
    "teres-major": ("Épaule et bras", ["back"], "Grand rond", "Teres major", "TMAJ", "intermediate", "#C026D3"),
    "triceps-brachii-long": ("Épaule et bras", ["back"], "Triceps brachial (chef long)", "Triceps brachii (long head)", "TBL", "superficial", "#7C3AED"),
    "triceps-brachii-lateral": ("Épaule et bras", ["back"], "Triceps brachial (chef latéral)", "Triceps brachii (lateral head)", "TBLat", "superficial", "#6D28D9"),
    "triceps-brachii-medial": ("Épaule et bras", ["back"], "Triceps brachial (chef médial)", "Triceps brachii (medial head)", "TBM", "intermediate", "#8B5CF6"),

    # Avant-bras et main
    "brachioradialis": ("Avant-bras et main", ["front"], "Brachio-radial", "Brachioradialis", "BR", "superficial", "#0891B2"),
    "pronator-teres": ("Avant-bras et main", ["front"], "Rond pronateur", "Pronator teres", "PT", "superficial", "#D97706"),
    "flexor-carpi-radialis": ("Avant-bras et main", ["front"], "Fléchisseur radial du carpe", "Flexor carpi radialis", "FCR", "superficial", "#16A34A"),
    "palmaris-longus": ("Avant-bras et main", ["front"], "Long palmaire", "Palmaris longus", "PL", "superficial", "#65A30D"),
    "flexor-carpi-ulnaris": ("Avant-bras et main", ["front"], "Fléchisseur ulnaire du carpe", "Flexor carpi ulnaris", "FCU", "superficial", "#4D7C0F"),
    "flexor-digitorum-superficialis": ("Avant-bras et main", ["front"], "Fléchisseur superficiel des doigts", "Flexor digitorum superficialis", "FDS", "intermediate", "#0284C7"),
    "abductor-pollicis-brevis": ("Avant-bras et main", ["front"], "Court abducteur du pouce", "Abductor pollicis brevis", "APB", "superficial", "#DB2777"),
    "abductor-digiti-minimi-hand": ("Avant-bras et main", ["front"], "Abducteur du petit doigt", "Abductor digiti minimi (hand)", "ADMh", "superficial", "#BE123C"),
    "extensor-carpi-radialis-longus": ("Avant-bras et main", ["back"], "Long extenseur radial du carpe", "Extensor carpi radialis longus", "ECRL", "superficial", "#3B82F6"),
    "extensor-carpi-radialis-brevis": ("Avant-bras et main", ["back"], "Court extenseur radial du carpe", "Extensor carpi radialis brevis", "ECRB", "intermediate", "#1D4ED8"),
    "extensor-digitorum": ("Avant-bras et main", ["back"], "Extenseur des doigts", "Extensor digitorum", "ED", "superficial", "#4338CA"),
    "extensor-carpi-ulnaris": ("Avant-bras et main", ["back"], "Extenseur ulnaire du carpe", "Extensor carpi ulnaris", "ECU", "superficial", "#6D28D9"),
    "dorsal-interossei-hand": ("Avant-bras et main", ["back"], "Interosseux dorsaux (main)", "Dorsal interossei (hand)", "DI", "deep", "#9F1239"),

    # Hanche et cuisse
    "tensor-fasciae-latae": ("Hanche et cuisse", ["front"], "Tenseur du fascia lata", "Tensor fasciae latae", "TFL", "superficial", "#8B5CF6"),
    "sartorius": ("Hanche et cuisse", ["front"], "Sartorius", "Sartorius", "SAR", "superficial", "#F59E0B"),
    "rectus-femoris": ("Hanche et cuisse", ["front"], "Droit fémoral", "Rectus femoris", "RF", "superficial", "#DC2626"),
    "vastus-lateralis": ("Hanche et cuisse", ["front"], "Vaste latéral", "Vastus lateralis", "VL", "intermediate", "#2563EB"),
    "vastus-medialis": ("Hanche et cuisse", ["front"], "Vaste médial", "Vastus medialis", "VM", "intermediate", "#059669"),
    "gracilis": ("Hanche et cuisse", ["front"], "Gracile", "Gracilis", "GRA", "superficial", "#0D9488"),
    "adductor-longus": ("Hanche et cuisse", ["front"], "Long adducteur", "Adductor longus", "ADL", "intermediate", "#9333EA"),
    "gluteus-maximus": ("Hanche et cuisse", ["back"], "Grand fessier", "Gluteus maximus", "GMAX", "superficial", "#B91C1C"),
    "gluteus-medius": ("Hanche et cuisse", ["back"], "Moyen fessier", "Gluteus medius", "GMED", "intermediate", "#C026D3"),
    "gluteus-minimus": ("Hanche et cuisse", ["back"], "Petit fessier", "Gluteus minimus", "GMIN", "deep", "#A21CAF"),
    "biceps-femoris-long": ("Hanche et cuisse", ["back"], "Biceps fémoral (chef long)", "Biceps femoris (long head)", "BFL", "superficial", "#7C3AED"),
    "biceps-femoris-short": ("Hanche et cuisse", ["back"], "Biceps fémoral (chef court)", "Biceps femoris (short head)", "BFS", "intermediate", "#9333EA"),
    "semitendinosus": ("Hanche et cuisse", ["back"], "Semi-tendineux", "Semitendinosus", "ST", "intermediate", "#0284C7"),
    "semimembranosus": ("Hanche et cuisse", ["back"], "Semi-membraneux", "Semimembranosus", "SM", "deep", "#4338CA"),
    "adductor-magnus": ("Hanche et cuisse", ["back"], "Grand adducteur", "Adductor magnus", "ADM", "deep", "#7E22CE"),

    # Jambe et pied
    "tibialis-anterior": ("Jambe et pied", ["front"], "Tibial antérieur", "Tibialis anterior", "TA", "superficial", "#16A34A"),
    "fibularis-longus": ("Jambe et pied", ["front"], "Long fibulaire", "Fibularis longus", "PL", "intermediate", "#059669"),
    "extensor-digitorum-longus": ("Jambe et pied", ["front"], "Long extenseur des orteils", "Extensor digitorum longus", "EDL", "intermediate", "#0891B2"),
    "extensor-digitorum-brevis": ("Jambe et pied", ["front"], "Court extenseur des orteils", "Extensor digitorum brevis", "EDB", "superficial", "#14B8A6"),
    "abductor-hallucis": ("Jambe et pied", ["front"], "Abducteur de l’hallux", "Abductor hallucis", "AH", "superficial", "#F43F5E"),
    "gastrocnemius-medial": ("Jambe et pied", ["back"], "Gastrocnémien médial", "Gastrocnemius medialis", "MG", "superficial", "#EA580C"),
    "gastrocnemius-lateral": ("Jambe et pied", ["back"], "Gastrocnémien latéral", "Gastrocnemius lateralis", "LG", "superficial", "#D97706"),
    "soleus": ("Jambe et pied", ["back"], "Soléaire", "Soleus", "SOL", "intermediate", "#CA8A04")
}
SECTIONS = ["Tête et cou", "Tronc", "Épaule et bras", "Avant-bras et main", "Hanche et cuisse", "Jambe et pied"]

WIDTH = int((X_RANGE[1] - X_RANGE[0]) * PX_PER_UNIT)
HEIGHT = int((Y_RANGE[1] - Y_RANGE[0]) * PX_PER_UNIT)
SCALE = OUT_PER_UNIT / PX_PER_UNIT


def load_meshes():
    scene = trimesh.load(GLB)
    meshes = {}
    for node in scene.graph.nodes_geometry:
        transform, name = scene.graph[node]
        geom = scene.geometry[name]
        verts = (np.c_[geom.vertices, np.ones(len(geom.vertices))] @ transform.T)[:, :3]
        meshes[name] = (verts, np.asarray(geom.faces))
    return meshes


def merge(components):
    offset, verts, faces = 0, [], []
    for c in components:
        verts.append(c.vertices)
        faces.append(c.faces + offset)
        offset += len(c.vertices)
    return np.vstack(verts), np.vstack(faces)


def derive_parts(meshes):
    parts = {k: v for k, v in meshes.items() if k in LAYOUT}

    def split_mesh(name, min_faces=20):
        verts, faces = meshes[name]
        return [c for c in trimesh.Trimesh(verts, faces, process=False).split(only_watertight=False) if len(c.faces) > min_faces]

    # 1. Gastrocnémien : médial = plus proche du plan sagittal x = 0, latéral = plus éloigné
    comps = split_mesh("gastrocnemius")
    medial, lateral = [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        side_comps.sort(key=lambda c: abs(c.vertices[:, 0].mean()))
        assert len(side_comps) >= 2, "gastrocnémien : chefs introuvables"
        medial.append(side_comps[0])
        lateral.append(side_comps[-1])
    parts["gastrocnemius-medial"] = merge(medial)
    parts["gastrocnemius-lateral"] = merge(lateral)

    # 2. Trapèze : 3 composantes connexes natives (triées par altitude Y croissante : inférieur, moyen, supérieur)
    comps = split_mesh("trapezius")
    trap_low, trap_mid, trap_up = [], [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        side_comps.sort(key=lambda c: c.vertices[:, 1].mean())
        assert len(side_comps) == 3, f"trapèze : 3 composantes attendues par côté, obtenu {len(side_comps)}"
        trap_low.append(side_comps[0])
        trap_mid.append(side_comps[1])
        trap_up.append(side_comps[2])
    parts["trapezius-lower"] = merge(trap_low)
    parts["trapezius-middle"] = merge(trap_mid)
    parts["trapezius-upper"] = merge(trap_up)

    # 3. Deltoïde : 3 chefs (antérieur AD, moyen / latéral MD, postérieur PD)
    # Tri sagittal Z : Z min = postérieur, Z max = antérieur, intermédiaire = moyen (|X| max)
    comps = split_mesh("deltoid")
    delt_ant, delt_mid, delt_post = [], [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        assert len(side_comps) == 3, f"deltoïde : 3 composantes attendues par côté, obtenu {len(side_comps)}"
        side_comps.sort(key=lambda c: c.vertices[:, 2].mean())
        delt_post.append(side_comps[0])
        delt_mid.append(side_comps[1])
        delt_ant.append(side_comps[2])
    parts["deltoid-anterior"] = merge(delt_ant)
    parts["deltoid-middle"] = merge(delt_mid)
    parts["deltoid-posterior"] = merge(delt_post)

    # 4. Biceps fémoral : 2 chefs (chef long BFL et chef court BFS)
    # Tri par hauteur / étendue verticale : le chef long naît sur l'ischion (plus haut, plus étendu)
    comps = split_mesh("biceps-femoris")
    bf_long, bf_short = [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        assert len(side_comps) == 2, f"biceps fémoral : 2 composantes attendues par côté, obtenu {len(side_comps)}"
        side_comps.sort(key=lambda c: (c.vertices[:, 1].max() - c.vertices[:, 1].min()))
        bf_short.append(side_comps[0])
        bf_long.append(side_comps[1])
    parts["biceps-femoris-long"] = merge(bf_long)
    parts["biceps-femoris-short"] = merge(bf_short)

    # 5. Triceps brachial : 3 chefs (long TBL, latéral TBLat, médial TBM)
    # Le chef médial naît plus bas sur l'humérus (Y moyen le plus bas).
    # Entre le long et le latéral : le latéral a le plus grand |X|, le long s'attache sur la scapula.
    comps = split_mesh("triceps-brachii")
    tb_long, tb_lat, tb_med = [], [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        assert len(side_comps) == 3, f"triceps brachial : 3 composantes attendues par côté, obtenu {len(side_comps)}"
        side_comps.sort(key=lambda c: c.vertices[:, 1].mean())
        med = side_comps[0]
        rem = side_comps[1:]
        rem.sort(key=lambda c: abs(c.vertices[:, 0].mean()))
        lon = rem[0]
        lat = rem[1]
        tb_med.append(med)
        tb_long.append(lon)
        tb_lat.append(lat)
    parts["triceps-brachii-long"] = merge(tb_long)
    parts["triceps-brachii-lateral"] = merge(tb_lat)
    parts["triceps-brachii-medial"] = merge(tb_med)

    # 6. Biceps brachial : 2 chefs (chef long BBL et chef court BBS)
    # Le chef court naît sur le processus coracoïde (médial, |X| plus faible).
    # Le chef long passe dans le sillon intertuberculaire (latéral, |X| plus élevé, tendon plus haut).
    comps = split_mesh("biceps-brachii")
    bb_long, bb_short = [], []
    for side in (-1, 1):
        side_comps = [c for c in comps if np.sign(c.vertices[:, 0].mean()) == side]
        assert len(side_comps) == 2, f"biceps brachial : 2 composantes attendues par côté, obtenu {len(side_comps)}"
        side_comps.sort(key=lambda c: abs(c.vertices[:, 0].mean()))
        bb_short.append(side_comps[0])
        bb_long.append(side_comps[1])
    parts["biceps-brachii-long"] = merge(bb_long)
    parts["biceps-brachii-short"] = merge(bb_short)

    return parts


def rasterize(verts, faces, view):
    x = verts[:, 0] if view == "front" else -verts[:, 0]
    px = (x - X_RANGE[0]) * PX_PER_UNIT
    py = (Y_RANGE[1] - verts[:, 1]) * PX_PER_UNIT
    tris = np.round(np.stack([px[faces], py[faces]], axis=-1) * 16).astype(np.int32)
    mask = np.zeros((HEIGHT, WIDTH), np.uint8)
    cv2.fillPoly(mask, list(tris), 255, lineType=cv2.LINE_8, shift=4)
    return mask


def ellipse(size):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))


def smooth_mask(mask, close=3, sigma=2.2):
    if close:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ellipse(2 * close + 1))
    return (cv2.GaussianBlur(mask, (0, 0), sigma) > 127).astype(np.uint8) * 255


def contour_path(mask, min_area=500, sigma=8.0, step=8, transform=None):
    """Contour externe lissé : filtre gaussien périodique des coordonnées, rééchantillonnage, courbes de Bézier (Catmull-Rom)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sx, sy, ox, oy = transform or (SCALE, SCALE, 0.0, 0.0)
    pieces = []
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            continue
        pts = contour[:, 0, :].astype(float)
        if len(pts) < 12:
            continue
        pts = gaussian_filter1d(pts, sigma, axis=0, mode="wrap")
        pts = pts[::max(1, int(step))]
        if len(pts) < 4:
            continue
        pts = pts * np.array([sx, sy]) + np.array([ox, oy])
        n = len(pts)
        d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
        for i in range(n):
            p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            c1 = p1 + (p2 - p0) / 6
            c2 = p2 - (p3 - p1) / 6
            d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
        pieces.append("".join(d) + "Z")
    return "".join(pieces)


def anchors(mask, center_x):
    """Composantes principales avec ligne médiane (une abscisse par ligne) pour les repères horizontaux."""
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count <= 1:
        return []
    biggest = stats[1:, cv2.CC_STAT_AREA].max()
    result = []
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] < max(biggest * 0.12, 400):
            continue
        x0, y0, w, h = stats[label, :4]
        component = labels[y0:y0 + h, x0:x0 + w] == label
        rows = []
        for ry in range(0, h, 6):
            xs = np.flatnonzero(component[ry])
            if xs.size == 0:
                continue
            breaks = np.flatnonzero(np.diff(xs) > 1)
            starts, ends = np.r_[0, breaks + 1], np.r_[breaks, xs.size - 1]
            k = int(np.argmax(ends - starts))
            rows.append([round((y0 + ry) * SCALE, 1), round(((xs[starts[k]] + xs[ends[k]]) / 2 + x0) * SCALE, 1)])
        if len(rows) < 2:
            continue
        cx, cy = centroids[label] * SCALE
        result.append({
            "cx": round(cx, 1), "cy": round(cy, 1),
            "y0": rows[0][0], "y1": rows[-1][0],
            "side": "L" if cx < center_x else "R",
            "rows": rows,
        })
    return result


WORKSPACE_HAND_REFINED = 'hand_nano_refined.jpg' if os.path.exists('hand_nano_refined.jpg') else '../AQ-Tech/MuscleAtlas/hand_nano_refined.jpg'


def draw_tapered_capsule(mask, p0, p1, r0, r1, val=255):
    p0, p1 = np.array(p0, dtype=float), np.array(p1, dtype=float)
    for t in np.linspace(0.0, 1.0, 100):
        p = p0 * (1 - t) + p1 * t
        r = r0 * (1 - t) + r1 * t
        cv2.circle(mask, (int(round(p[0] * 16)), int(round(p[1] * 16))), int(round(r * 16)), val, -1, lineType=cv2.LINE_AA, shift=4)


def build_final_silhouette(base_mask):
    """Silhouette corporelle anatomique de référence avec mains 5 doigts haute définition et pieds réalistes."""
    m = base_mask.copy()

    # 1. MAINS : mains 5 doigts haute définition (hand_nano_refined.jpg)
    if os.path.exists(WORKSPACE_HAND_REFINED):
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

        for sy in range(50, 500):
            dy = 1950 + sy
            for sx in range(410):
                if mask_ref_500[sy, sx] > 0:
                    dx = 20 + sx
                    m[dy, dx] = 255

        hand_band = m[1985:2450, :870].astype(np.float32)
        hand_band = cv2.GaussianBlur(hand_band, (9, 9), 2.0)
        m[1985:2450, :870] = (hand_band > 127).astype(np.uint8) * 255

    # 2. PIEDS : arche médiale et cascade anatomique des orteils D1 -> D5 (côté gauche)
    draw_tapered_capsule(m, (722, 3800), (730, 4005), 11.0, 20.0, 255)  # Hallux (D1)
    draw_tapered_capsule(m, (728, 4006), (674, 4008), 20.0, 18.5, 255)  # Hallux -> D2
    draw_tapered_capsule(m, (674, 4008), (618, 4004), 18.5, 16.0, 255)  # D2 -> D3
    draw_tapered_capsule(m, (618, 4004), (554, 3997), 16.0, 15.0, 255)  # D3 -> arrondi D5

    foot_band = m[3660:4060, :870].astype(np.float32)
    foot_band = cv2.GaussianBlur(foot_band, (21, 21), 4.5)
    m[3660:4060, :870] = (foot_band > 127).astype(np.uint8) * 255

    # 3. SYMÉTRIE BILATÉRALE PARFAITE : le côté droit est la réflexion mathématique exacte du côté gauche
    m[:, 870:] = np.fliplr(m[:, :870])
    return m


def vectorize_body_mask(mask):
    """Vectorisation continue haute résolution avec courbes de Bézier cubiques régulières."""
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


def body_union(meshes, view):
    union = np.zeros((HEIGHT, WIDTH), np.uint8)
    for k, (verts, faces) in meshes.items():
        if k in ('tibialis-posterior', 'flexor-digitorum-longus'):
            continue
        union = cv2.bitwise_or(union, rasterize(verts, faces, view))
    return union


def fill_holes(mask):
    flood = cv2.bitwise_not(mask)
    cv2.floodFill(flood, np.zeros((HEIGHT + 2, WIDTH + 2), np.uint8), (0, 0), 0)
    return cv2.bitwise_or(mask, flood)


def body_silhouette_base(union):
    union = cv2.morphologyEx(union, cv2.MORPH_CLOSE, ellipse(13))
    union = fill_holes(union)
    union = smooth_mask(union, close=0, sigma=5)
    union = cv2.dilate(union, ellipse(9))
    return smooth_mask(union, close=0, sigma=4)


def main():
    meshes = load_meshes()
    parts = derive_parts(meshes)
    center_x = (X_RANGE[1] - X_RANGE[0]) * OUT_PER_UNIT / 2
    data = {
        "viewBox": [0, 0, round((X_RANGE[1] - X_RANGE[0]) * OUT_PER_UNIT, 1), round((Y_RANGE[1] - Y_RANGE[0]) * OUT_PER_UNIT, 1)],
        "sections": SECTIONS,
        "views": {},
        "muscles": [],
    }

    technosport_colors = {}
    try:
        colors_file = Path(__file__).resolve().parent.parent / "technosport_muscle_colors.json"
        if colors_file.exists():
            with open(colors_file, "r", encoding="utf-8") as f:
                technosport_colors = {k: v["color"] for k, v in json.load(f).items()}
    except Exception:
        pass

    # Génération officielle de la silhouette corporelle haute définition
    u_front = body_union(meshes, "front")
    base_front = body_silhouette_base(u_front)
    mask_front = build_final_silhouette(base_front)
    mask_back = np.fliplr(mask_front)
    body_paths = {
        "front": vectorize_body_mask(mask_front),
        "back": vectorize_body_mask(mask_back),
    }

    for view in ("front", "back"):
        mask_view = mask_front if view == "front" else mask_back
        ys = np.flatnonzero(mask_view.any(axis=1))
        xs = np.flatnonzero(mask_view.any(axis=0))
        # Entrejambe : première ligne (depuis le bas) où la zone centrale ne forme plus qu'une plage
        half = int(0.45 * PX_PER_UNIT)
        band = mask_view[:, WIDTH // 2 - half: WIDTH // 2 + half] > 0
        crotch = next((r for r in range(ys[-1], ys[0], -1)
                       if band[r].any() and (np.diff(np.flatnonzero(band[r])) > 1).sum() == 0), None)
        data["views"][view] = {
            "body": body_paths[view],
            "bbox": [round(xs[0] * SCALE, 1), round(ys[0] * SCALE, 1), round(xs[-1] * SCALE, 1), round(ys[-1] * SCALE, 1)],
            "crotch": round(crotch * SCALE, 1) if crotch else None,
        }

    # Pré-calcul des masques et intersections 2D (overlaps) pour chaque vue
    muscle_masks = {"front": {}, "back": {}}
    for key, (section, views, fr, en, abbr, layer, color) in LAYOUT.items():
        verts, faces = parts[key]
        for view in views:
            mask = smooth_mask(rasterize(verts, faces, view), close=5, sigma=3.5)
            if key == 'extensor-digitorum-brevis' and view == 'front' and 'extensor-hallucis-brevis' in meshes:
                v2, f2 = meshes['extensor-hallucis-brevis']
                mask = cv2.bitwise_or(mask, smooth_mask(rasterize(v2, f2, 'front'), close=5, sigma=3.5))
            elif key == 'extensor-digitorum-longus' and view == 'front' and 'extensor-hallucis-longus' in meshes:
                v2, f2 = meshes['extensor-hallucis-longus']
                mask = cv2.bitwise_or(mask, smooth_mask(rasterize(v2, f2, 'front'), close=5, sigma=3.5))
            elif key in ('flexor-digitorum-superficialis', 'extensor-digitorum'):
                view_k = 'front' if key == 'flexor-digitorum-superficialis' else 'back'
                if view == view_k:
                    m_comb = mask.copy()
                    for is_right in [False, True]:
                        def tx_t(x):
                            return (1739.0 - x) if is_right else x
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
                    mask = smooth_mask(m_comb, close=5, sigma=3.5)
            muscle_masks[view][key] = mask

    overlaps = {"front": {}, "back": {}}
    for view in ("front", "back"):
        keys_in_view = list(muscle_masks[view].keys())
        small_masks = {
            k: (cv2.resize(muscle_masks[view][k], (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_NEAREST) > 0)
            for k in keys_in_view
        }
        for k1 in keys_in_view:
            m1 = small_masks[k1]
            overlaps[view][k1] = [k2 for k2 in keys_in_view if k1 != k2 and np.logical_and(m1, small_masks[k2]).any()]

    for key, (section, views, fr, en, abbr, layer, color) in LAYOUT.items():
        entry = {
            "id": key,
            "section": section,
            "fr": fr,
            "en": en,
            "abbr": abbr,
            "layer": layer,
            "color": technosport_colors.get(key, color),
            "technosport_color": technosport_colors.get(key, color),
            "views": {}
        }
        verts, faces = parts[key]
        for view in views:
            mask = muscle_masks[view][key]
            path = contour_path(mask)
            if not path:
                continue
            sign = 1 if view == "front" else -1
            depth = float((sign * verts[:, 2])[np.unique(faces)].mean())
            entry["views"][view] = {
                "d": path,
                "depth": round(depth, 3),
                "anchors": anchors(mask, center_x),
                "overlaps": overlaps[view].get(key, []),
            }
        data["muscles"].append(entry)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(len(data["muscles"]), "muscles traités,", round(len(json.dumps(data)) / 1e6, 2), "Mo enregistrés dans", OUT)
    print({v: (data["views"][v]["crotch"], data["views"][v]["bbox"]) for v in data["views"]})


if __name__ == "__main__":
    main()
