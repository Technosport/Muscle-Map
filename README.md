# Muscle Map — Cartographie anatomique vectorielle sEMG 2D

Application de référence (autonome, sans CDN) : ouvrir `index.html` dans un navigateur.

## Utilisation
- **Réglages** : fond (blanc / noir / transparent), corps (clair / foncé), vue (duo, face, dos ; entier, haut, bas), repères (aucun, N°, noms, N° + noms), langue FR / EN.
- **Liste de muscles** : sélection interactive, recherche ou import d'activations % CMLV / % MVC (JSON). Abréviations acceptées (VL, VM, RF, BF, MG, LG, TA…).
- **Avec valeurs** : heatmap 0–100 % MVC avec barre thermique. Sans valeur : mode classique avec muscles sélectionnés (protocole).
- **Export haute qualité adaptatif** :
  - **Format intelligent (Auto-Fit)** : cadrage géométrique serré sans marges inutiles (évite tout rognage manuel).
  - **Sélecteur de ratios standards** : Auto (optimal), 16:9 (slide / présentation), 4:3 (publication), 9:16 (vertical / mobile), 3:4, ou 1:1 (carré hérité).
  - **SVG** (vectoriel haute définition jusqu'à 2048 px)
  - **PNG** (4K ultra haute définition jusqu'à 4096 px)
  - **Nommage des fichiers exportés** (la couleur est positionnée en dernier) :
    - En Français : `muscle-map_[vue]_[zone](_[mode])(_[ratio])_[fond].[ext]` (ex: `muscle-map_duo_fullbody_white.png`, `muscle-map_face_upperbody_16x9_black.svg`, `muscle-map_dos_lowerbody_cmlv_transparent.png`)
    - En Anglais : `muscle-map_[vue]_[zone](_[mode])(_[ratio])_[fond].[ext]` (ex: `muscle-map_duo_fullbody_white.png`, `muscle-map_front_upperbody_16x9_black.svg`, `muscle-map_back_lowerbody_mvc_transparent.png`)

## Reconstruction
Pour régénérer `index.html` après modification du gabarit `app.template.html` :
```bash
python build_app.py
```
*(Ne pas éditer `index.html` manuellement car il est compilé à partir de `app.template.html` et `atlas_data.json`).*

## Déploiement GitHub Pages
Ce dépôt est directement compatible avec GitHub Pages sans configuration complexe :
1. Pousser ce dossier vers un dépôt GitHub (ex. `MuscleMap`).
2. Dans GitHub, aller dans **Settings > Pages**.
3. Sous **Branch**, sélectionner `main` et le dossier `/ (root)`.
4. L'application sera accessible publiquement via l'URL `https://<votre-compte>.github.io/MuscleMap/`.

## Référence anatomique
- Tracés anatomiques issus de la projection des maillages BodyParts3D (CC BY-SA 2.1 JP, DBCLS).
