"""Projette les maillages BodyParts3D (face / dos) en tracés vectoriels lissés pour l'atlas sEMG.

Sortie : MuscleAtlas/atlas_data.json (contour du corps + un tracé par muscle et par vue).
Usage : python MuscleAtlas/build_atlas_data.py   (depuis la racine du projet)
"""
import os
import json
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter1d
import trimesh

GLB = "MuscleStudio/muscles.glb"
OUT = "MuscleAtlas/atlas_data.json"

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
    "deltoid": ("Épaule et bras", ["front", "back"], "Deltoïde", "Deltoid", "DEL", "superficial", "#F97316"),
    "biceps-brachii": ("Épaule et bras", ["front"], "Biceps brachial", "Biceps brachii", "BB", "superficial", "#2563EB"),
    "infraspinatus": ("Épaule et bras", ["back"], "Infra-épineux", "Infraspinatus", "INF", "intermediate", "#9333EA"),
    "teres-major": ("Épaule et bras", ["back"], "Grand rond", "Teres major", "TMAJ", "intermediate", "#C026D3"),
    "triceps-brachii": ("Épaule et bras", ["back"], "Triceps brachial", "Triceps brachii", "TB", "superficial", "#7C3AED"),

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
    "biceps-femoris": ("Hanche et cuisse", ["back"], "Biceps fémoral", "Biceps femoris", "BF", "superficial", "#7C3AED"),
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

# Découpage géométrique approximatif du trapèze (altitude du centroïde de chaque triangle, repère du modèle)
TRAPEZIUS_CUTS = (1.95, 1.45)

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

    # Gastrocnémien : composantes connexes ; médial = plus proche du plan sagittal x = 0
    verts, faces = meshes["gastrocnemius"]
    components = trimesh.Trimesh(verts, faces, process=False).split(only_watertight=False)
    medial, lateral = [], []
    for side in (-1, 1):
        side_components = [c for c in components if np.sign(c.vertices[:, 0].mean()) == side]
        side_components.sort(key=lambda c: abs(c.vertices[:, 0].mean()))
        assert len(side_components) >= 2, "gastrocnémien : chefs introuvables"
        medial.append(side_components[0])
        lateral.append(side_components[-1])
    parts["gastrocnemius-medial"] = merge(medial)
    parts["gastrocnemius-lateral"] = merge(lateral)

    verts, faces = meshes["trapezius"]
    centroid_y = verts[faces].mean(axis=1)[:, 1]
    upper_cut, lower_cut = TRAPEZIUS_CUTS
    parts["trapezius-upper"] = (verts, faces[centroid_y >= upper_cut])
    parts["trapezius-middle"] = (verts, faces[(centroid_y < upper_cut) & (centroid_y >= lower_cut)])
    parts["trapezius-lower"] = (verts, faces[centroid_y < lower_cut])
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


def contour_path_v1(mask, min_area=30, epsilon=0.9):
    """Tracé de la 1re version : polygone simplifié + courbes quadratiques par points milieux."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pieces = []
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            continue
        points = cv2.approxPolyDP(contour, epsilon, True)[:, 0, :].astype(float) * SCALE
        if len(points) < 3:
            continue
        mids = (points + np.roll(points, -1, axis=0)) / 2
        d = [f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f}"]
        for p, m in zip(points, mids):
            d.append(f"Q{p[0]:.1f} {p[1]:.1f} {m[0]:.1f} {m[1]:.1f}")
        pieces.append("".join(d) + "Z")
    return "".join(pieces)


def body_union(meshes, view):
    union = np.zeros((HEIGHT, WIDTH), np.uint8)
    for verts, faces in meshes.values():
        union = cv2.bitwise_or(union, rasterize(verts, faces, view))
    return union


def fill_holes(mask):
    flood = cv2.bitwise_not(mask)
    cv2.floodFill(flood, np.zeros((HEIGHT + 2, WIDTH + 2), np.uint8), (0, 0), 0)
    return cv2.bitwise_or(mask, flood)


def body_silhouette(union):
    union = cv2.morphologyEx(union, cv2.MORPH_CLOSE, ellipse(5))
    union = fill_holes(union)
    union = smooth_mask(union, close=0, sigma=5)
    union = cv2.dilate(union, ellipse(9))
    return smooth_mask(union, close=0, sigma=4)


def body_silhouette_v1(union):
    union = cv2.morphologyEx(union, cv2.MORPH_CLOSE, ellipse(13))
    union = fill_holes(union)
    union = smooth_mask(union, close=0, sigma=5)
    union = cv2.dilate(union, ellipse(9))
    return smooth_mask(union, close=0, sigma=4)


def extract_human_contour(view, margin_px=0):
    """Extrait la silhouette humaine anatomique réaliste avec vraies mains (5 doigts), vrais pieds (talon, orteils),
    calée avec exactitude sur le repère de l'atlas sEMG, avec une marge respirante optionnelle."""
    mask_path = f"MuscleAtlas/realistic_{view}_mask.png"
    if os.path.exists(mask_path):
        solid = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(f"MuscleStudio/outlines/{view}.png", cv2.IMREAD_UNCHANGED)
        alpha = (img[:, :, 3] > 60).astype(np.uint8) * 255
        closed = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        flood = cv2.bitwise_not(closed)
        h, w = flood.shape
        cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 0)
        solid = cv2.bitwise_or(closed, flood)
    
    if margin_px > 0:
        # Dilatation intelligente : donne la marge respirante au tronc et membres tout en préservant 100% de la découpe des doigts et orteils
        body_core = solid.copy()
        body_core[1160:, :235] = 0
        body_core[1160:, 733:] = 0
        body_core[2280:, :] = 0
        k = margin_px * 2 + 1
        dilated_core = cv2.dilate(body_core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        
        extremities = solid.copy()
        extremities[:1160, :] = 0
        extremities[1400:2280, :] = 0
        
        solid = cv2.bitwise_or(dilated_core, extremities)
        smoothed = cv2.GaussianBlur(solid.astype(np.float32), (3, 3), 0.7)
        solid = (smoothed > 127).astype(np.uint8) * 255
        
    contours, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    main_c = max(contours, key=cv2.contourArea)[:, 0, :].astype(float)
    
    y_min, y_max = main_c[:, 1].min(), main_c[:, 1].max()
    cx = (main_c[:, 0].min() + main_c[:, 0].max()) / 2.0
    
    # Calage anatomique sur l'axe sagittal et la hauteur tête-pieds de l'atlas
    scale_y = (669.8 - 10.0) / (y_max - y_min)
    scale_x = scale_y
    
    pts = np.zeros_like(main_c)
    pts[:, 1] = 10.0 + (main_c[:, 1] - y_min) * scale_y
    pts[:, 0] = 145.0 + (main_c[:, 0] - cx) * scale_x
    
    # Lissage doux (sigma=1.2) pour conserver 100% du détail des doigts et des orteils
    pts = gaussian_filter1d(pts, 1.2, axis=0, mode='wrap')
    pts = pts[::2]
    
    n = len(pts)
    d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6
        c2 = p2 - (p3 - p1) / 6
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(d) + "Z"


def ai_outline(view, union):
    """Contour historique de MuscleStudio."""
    img = cv2.imread(f"MuscleStudio/outlines/{view}.png", cv2.IMREAD_UNCHANGED)
    mask = (img[:, :, 3] > 100).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ellipse(9))
    flood = cv2.bitwise_not(mask)
    cv2.floodFill(flood, np.zeros((mask.shape[0] + 2, mask.shape[1] + 2), np.uint8), (0, 0), 0)
    mask = cv2.bitwise_or(mask, flood)
    uy, ux = np.nonzero(union)
    x0, x1, y0, y1 = ux.min() * SCALE, (ux.max() + 1) * SCALE, uy.min() * SCALE, (uy.max() + 1) * SCALE
    pad_x, pad_y = (x1 - x0) * 0.012, (y1 - y0) * 0.012
    x0, x1, y0, y1 = x0 - pad_x, x1 + pad_x, y0 - pad_y, y1 + pad_y
    h, w = mask.shape
    return contour_path(mask, min_area=5000, sigma=22, step=14, transform=((x1 - x0) / w, (y1 - y0) / h, x0, y0))


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

    for view in ("front", "back"):
        union = body_union(meshes, view)
        silhouette = body_silhouette(union)
        silhouette_v1 = body_silhouette_v1(union)
        ys = np.flatnonzero(silhouette.any(axis=1))
        xs = np.flatnonzero(silhouette.any(axis=0))
        # Entrejambe : première ligne (depuis le bas) où la zone centrale ne forme plus qu'une plage
        half = int(0.45 * PX_PER_UNIT)
        band = silhouette[:, WIDTH // 2 - half: WIDTH // 2 + half] > 0
        crotch = next((r for r in range(ys[-1], ys[0], -1)
                       if band[r].any() and (np.diff(np.flatnonzero(band[r])) > 1).sum() == 0), None)
        data["views"][view] = {
            "human_margin": extract_human_contour(view, margin_px=9),
            "human": extract_human_contour(view, margin_px=0),
            "body": contour_path(silhouette, min_area=2000, sigma=5, step=5),
            "body_v1": contour_path_v1(silhouette_v1, min_area=2000, epsilon=1.2),
            "ai": ai_outline(view, union),
            "bbox": [round(xs[0] * SCALE, 1), round(ys[0] * SCALE, 1), round(xs[-1] * SCALE, 1), round(ys[-1] * SCALE, 1)],
            "crotch": round(crotch * SCALE, 1) if crotch else None,
        }

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
            mask = smooth_mask(rasterize(verts, faces, view), close=5, sigma=3.5)
            path = contour_path(mask)
            if not path:
                continue
            sign = 1 if view == "front" else -1
            depth = float((sign * verts[:, 2])[np.unique(faces)].mean())
            entry["views"][view] = {
                "d": path,
                "d_v1": contour_path_v1(smooth_mask(rasterize(verts, faces, view))),
                "depth": round(depth, 3),
                "anchors": anchors(mask, center_x),
            }
        data["muscles"].append(entry)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(len(data["muscles"]), "muscles traités,", round(len(json.dumps(data)) / 1e6, 2), "Mo enregistrés dans", OUT)
    print({v: (data["views"][v]["crotch"], data["views"][v]["bbox"]) for v in data["views"]})


if __name__ == "__main__":
    main()
