# Muscle Map — Cartographie anatomique vectorielle sEMG 2D

[![Deploy to GitHub Pages](https://github.com/Technosport/Muscle-Map/actions/workflows/deploy.yml/badge.svg)](https://github.com/Technosport/Muscle-Map/actions/workflows/deploy.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](index.html)
[![License](https://img.shields.io/badge/license-CC--BY--SA--2.1--JP-green.svg)](https://creativecommons.org/licenses/by-sa/2.1/jp/)

Application autonome de référence pour le laboratoire : cartographie anatomique 2D haute résolution pour l'illustration de protocoles d'électromyographie de surface (sEMG) et la visualisation de résultats normalisés (% CMLV / % MVC).

---

## 🚀 Utilisation immédiate

### 1. En ligne (GitHub Pages)
Accessible directement sur n'importe quel appareil (PC, Mac, tablette, smartphone) sans installation :
👉 **`https://technosport.github.io/Muscle-Map/`**

### 2. En local au laboratoire (Hors-ligne)
Sur un poste d'acquisition (Noraxon, Delsys, etc.) sans connexion internet :
- Télécharger ou copier ce dossier sur le poste.
- Faire un **double-clic sur `index.html`** dans votre navigateur (Chrome, Edge, Firefox, Safari).
- Aucun serveur ni connexion web n'est requis : l'application est 100 % autonome (~1.4 Mo, sans CDN).

---

## 🎨 Fonctionnalités principales

- **Modes de travail** :
  - **Mode Protocole (Classique)** : sélection interactive des muscles étudiés, palette anatomique ou rouge uniforme.
  - **Mode Résultats (Heatmap % CMLV / % MVC)** : coloration thermique dynamique 0–100 % avec échelle et tableau de valeurs en direct. Import/Export JSON d'activations avec support des abréviations standards (VL, VM, RF, BF, MG, LG, TA, GM, etc.).
- **Vues & Cadrage** :
  - Angles : Duo (Face + Dos), Face seule, Dos seul.
  - Cadrage : Corps entier, Haut du corps, Membres inférieurs.
  - Formats d'export adaptatifs (**Auto-Fit**) : Auto (optimal sans marges), 16:9 (slides), 4:3 (articles), 9:16 (vertical/mobile), 3:4, ou 1:1.
- **Rendu & Thème** :
  - Fond blanc, noir ou transparent (damier de repérage).
  - Silhouette claire ou foncée.
  - Repères anatomiques : N°, Noms des muscles, ou N° + Noms.
  - Bilingue complet : Français (FR) / Anglais (EN).
- **Export haute fidélité** :
  - **SVG vectoriel** (jusqu'à 2048 px) pour intégration vectorielle dans Illustrator, PowerPoint ou LaTeX.
  - **PNG 4K ultra haute définition** (jusqu'à 4096 px) prêt pour publication scientifique.
  - Nommage normalisé automatique (ex. `muscle-map_duo_fullbody_white.png`, `muscle-map_front_upperbody_16x9_black.svg`).
- **Raccourcis clavier** :
  - `P` : Afficher / Masquer le volet Paramètres.
  - `M` : Afficher / Masquer le volet Muscles.
  - `Molette` ou `+` / `-` : Zoom interactif.
  - `Double-clic` ou bouton `↺` : Réinitialiser la vue.

---

## 📦 Structure du dépôt

```text
MuscleMap/
├── .github/workflows/
│   └── deploy.yml              # Déploiement automatique GitHub Pages
├── .gitignore                  # Exclusions Git propres
├── .nojekyll                   # Indispensable pour GitHub Pages statique
├── README.md                   # Ce guide de documentation
├── index.html                  # 🌟 Application finale 100% autonome
├── app.template.html           # Gabarit source (HTML/CSS/JS)
├── muscle_map_data.json        # Base de données vectorielle des muscles et silhouettes
├── build_app.py                # Script de compilation autonome
├── muscles.glb                 # Maillages 3D sources BodyParts3D (archive de reconstruction)
├── hand_nano_refined.jpg       # Calque de détail des extrémités
├── build_atlas_data.py         # Script d'extraction vectorielle 3D -> 2D
└── refine_publication_contours.py # Raffinement géométrique des contours de publication
```

---

## 🛠️ Développement & Reconstruction

Si vous modifiez le gabarit `app.template.html` ou les données vectorielles `muscle_map_data.json` :

```bash
python build_app.py
```

Le script réinjecte les données dans `index.html` en une fraction de seconde.

> **Note :** Ne pas éditer manuellement `index.html`, toutes les modifications d'interface doivent être faites dans `app.template.html`.

---

## 🌐 Déploiement sur GitHub Pages (Pas à pas)

1. **Créer le dépôt GitHub** :
   Créez un nouveau dépôt public (ou privé avec GitHub Pro/Enterprise) nommé `MuscleMap` sur votre compte ou organisation de laboratoire.

2. **Pousser le code** :
   ```bash
   git push -u origin main
   ```

3. **Activer GitHub Pages** :
   - Rendez-vous sur votre dépôt GitHub dans **Settings > Pages** : [https://github.com/Technosport/Muscle-Map/settings/pages](https://github.com/Technosport/Muscle-Map/settings/pages).
   - Sous **Build and deployment > Source** :
     - Choisissez **GitHub Actions** (le workflow `.github/workflows/deploy.yml` inclus prend tout en charge automatiquement à chaque push).
     - *Ou bien* choisissez **Deploy from a branch** avec la branche `main` et le dossier `/ (root)`.
   - Votre application sera en ligne à l'adresse : **`https://technosport.github.io/Muscle-Map/`**.

---

## 📚 Référence anatomique, Auteur & Crédits

- **Conception & Développement** : Jean PANCHAIRI (Technosport — Aix-Marseille Université)
- **Tracés anatomiques** : Issus de la projection des maillages **BodyParts3D 3.0** (Database Center for Life Science - DBCLS).
- **Mention de licence & attribution** : `Technosport amU · D'après BodyParts3D (DBCLS, CC BY-SA 2.1 JP)` (FR) / `Technosport amU · Based on BodyParts3D (DBCLS, CC BY-SA 2.1 JP)` (EN) sous [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/).
- Application conçue pour la recherche et l'enseignement en biomécanique, ergonomie et physiologie du sport.
