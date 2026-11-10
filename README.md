# Muscle Map

[![Technosport amU](https://img.shields.io/badge/Technosport-amU%20%7C%20ISM-002D62?style=flat-square)](https://github.com/Technosport)
[![Type](https://img.shields.io/badge/Type-Application%20Web%20autonome-009EE2?style=flat-square)](#)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-D%C3%A9ploy%C3%A9-26A669?style=flat-square)](https://technosport.github.io/Muscle-Map/)

> **Cartographie anatomique vectorielle 2D pour l'illustration de protocoles d'électromyographie de surface (sEMG) et la visualisation des niveaux d'activation (% CMV).**  
> *Développé au sein du **Technosport / ISM** (UMR 7287 CNRS — Aix-Marseille Université) • [**Application en ligne**](https://technosport.github.io/Muscle-Map/)*

<p align="center">
  <img src="docs/screenshots/muscle-map-heatmap.png" alt="Muscle Map — Visualisation thermique d'activation musculaire sEMG" width="100%">
</p>

---

## 🚀 Démarrage

### Accès en ligne (GitHub Pages)
- **Accès direct (Web)** : **[technosport.github.io/Muscle-Map](https://technosport.github.io/Muscle-Map/)**

### Utilisation locale
1. Télécharger ou cloner ce dépôt sur la machine.
2. Double-cliquer sur le fichier **`index.html`** dans un navigateur (Chrome, Edge, Firefox, Safari).

> [!NOTE]
> L'application est 100% autonome (~1.5 Mo) : elle fonctionne intégralement hors-ligne, sans dépendance externe, sans appel CDN et sans serveur web local requis.

---

## 🛠️ Fonctionnalités & Contenu

<p align="center">
  <img src="docs/screenshots/muscle-map-protocole.png" alt="Muscle Map — Mode protocole et sélection anatomique" width="100%">
</p>

| Module / Fonctionnalité | Description |
| :--- | :--- |
| **Mode Protocole (Classique)** | Sélection interactive parmi 63 muscles anatomiques, coloration par famille ou unicolore, et repères visuels (N°, Noms ou N° + Noms). |
| **Mode Résultats (Heatmap % CMV)** | Cartographie thermique dynamique continue (0 à 100 % CMV / % MVC) avec échelle chromatique paramétrable et jauges d'activation en direct. |
| **Vues & Cadrages** | Angles anatomiques (Duo Face + Dos, Face seule, Dos seul) et cadrages adaptatifs (Corps entier, Haut du corps, Membres inférieurs). |
| **Formats & Ratios** | Rendu automatique sans marges (Auto-Fit) ou ratios prédéfinis pour publications scientifiques et présentations (16:9, 4:3, 9:16, 3:4, 1:1). |
| **Export Vectoriel & 4K** | Export direct en **SVG vectoriel** (jusqu'à 2048 px) pour Illustrator / PowerPoint / LaTeX et en **PNG haute résolution** (jusqu'à 4096 px). |
| **Import / Export JSON** | Importation et exportation de jeux de données d'activation avec reconnaissance des abréviations sEMG standards (VL, VM, RF, BF, MG, LG, TA, GM, etc.). |
| **Bilingue FR / EN** | Interface complète et légendes exportées commutables instantanément en Français ou en Anglais. |

<details>
<summary><b>Voir les raccourcis clavier et contrôles interactifs</b></summary>

- `P` : Afficher ou masquer le volet de configuration (gauche).
- `M` : Afficher ou masquer le volet des muscles et activations (droite).
- `Molette souris` ou touches `+` / `-` : Zoom continu sur la planche anatomique.
- `Double-clic` ou bouton `↺` : Réinitialiser la vue et le centrage.

</details>

<details>
<summary><b>Voir le format JSON pour l'import d'activations (% CMV)</b></summary>

L'application accepte indifféremment les identifiants anatomiques complets ou les abréviations sEMG usuelles :

```json
{
  "mesures": [
    { "muscle": "vastus-lateralis", "cmv": 78.5 },
    { "muscle": "VM", "cmv": 65.0 },
    { "muscle": "RF", "cmv": 52.0 },
    { "muscle": "gastrocnemius-medial", "cmv": 46.0 },
    { "muscle": "BF", "cmv": 42.5 },
    { "muscle": "SOL", "cmv": 38.0 },
    { "muscle": "ST", "cmv": 37.0 },
    { "muscle": "TA", "cmv": 29.0 }
  ]
}
```

</details>

---

## 🔧 Structure du dépôt

| Fichier / Dossier | Rôle dans le projet |
| :--- | :--- |
| **`index.html`** | Application finale autonome et monolithique distribuable (embarquant styles, logique, logos et atlas vectoriel 2D). |
| **`favicon.*` / `apple-touch-icon.png`** | Jeux complet d'icônes et favicons pour l'application web. |
| **`docs/screenshots/`** | Captures d'écran officielles illustrant les fonctionnalités dans la documentation. |
| **`.github/workflows/deploy.yml`** | Workflow d'intégration et déploiement continu automatique sur GitHub Pages. |
