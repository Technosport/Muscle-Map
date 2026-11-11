# Muscle Map

[![Technosport amU](https://img.shields.io/badge/Technosport-amU%20%7C%20ISM-002D62?style=flat-square)](https://github.com/Technosport)
[![Type](https://img.shields.io/badge/Type-Standalone%20Web%20App-009EE2?style=flat-square)](#)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-Live-26A669?style=flat-square)](https://technosport.github.io/Muscle-Map/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24146734-blue?style=flat-square)](https://doi.org/10.5281/zenodo.24146734)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow?style=flat-square)](LICENSE)
[![Data License: CC BY-SA 2.1 JP](https://img.shields.io/badge/Atlas%20License-CC%20BY--SA%202.1%20JP-lightgrey?style=flat-square)](NOTICE.md)

> **Interactive 2D vector anatomical atlas for surface electromyography (sEMG) protocol illustration and muscle activation level visualization (% MVC).**  
> *Developed at **Technosport / ISM** (UMR 7287 CNRS — Aix-Marseille Université) • [**Launch Web Application**](https://technosport.github.io/Muscle-Map/)*

<p align="center">
  <img src="docs/screenshots/muscle-map-heatmap.png" alt="Muscle Map — Surface EMG muscle activation heatmap visualization" width="100%">
</p>

---

## 🚀 Getting Started

### Online Access (GitHub Pages)
- **Direct Web Access**: **[technosport.github.io/Muscle-Map](https://technosport.github.io/Muscle-Map/)**

### Offline / Local Usage
1. Clone or download this repository.
2. Double-click the standalone **`index.html`** file in any modern web browser (Chrome, Edge, Firefox, Safari).

> [!NOTE]
> The application is **100% standalone and monolithic (~1.5 MB)**: it runs completely offline with zero external dependencies, no CDN calls, no npm build step, and no local web server required.

---

## 🛠️ Features & Highlights

<p align="center">
  <img src="docs/screenshots/muscle-map-protocole.png" alt="Muscle Map — Protocol mode and anatomical muscle selection" width="100%">
</p>

| Module / Feature | Description |
| :--- | :--- |
| **Protocol Mode (Classic)** | Interactive selection of 63 anatomical muscles, customizable color families or monochrome, and flexible visual callouts (Numbers, Names, or Numbers + Names). |
| **Results Mode (% MVC Heatmap)** | Continuous dynamic thermal heatmap (0 to 100% MVC / % CMV) with adjustable color scales and real-time live activation gauges. |
| **Views & Framings** | Anatomical angles (Dual Anterior + Posterior, Anterior only, Posterior only) and adaptive framings (Full body, Upper body, Lower limbs). |
| **Publication Aspect Ratios** | Auto-Fit (tight bounding box without wasted margins) or standardized publication ratios (16:9, 4:3, 9:16, 3:4, 1:1). |
| **Vector & High-Res Export** | Direct export to **vector SVG** (up to 2048 px) for Adobe Illustrator / PowerPoint / LaTeX and **high-definition PNG** (up to 4096 px) with embedded citation metadata. |
| **JSON Import / Export** | Batch import and export of muscle activation values with automatic recognition of standard sEMG abbreviations (VL, VM, RF, BF, MG, LG, TA, GM, etc.). |
| **Bilingual Interface (EN / FR)** | Switch the entire user interface and exported legends between English and French with a single click. |

<details>
<summary><b>Keyboard Shortcuts & Navigation Controls</b></summary>

- `P` : Toggle settings configuration drawer (left).
- `M` : Toggle muscle and activation drawer (right).
- `Mouse Wheel` or `+` / `-` keys : Smooth continuous zoom on the anatomical board.
- `Double-click` or `↺` button : Reset zoom level and center view.

</details>

<details>
<summary><b>JSON Format for % MVC Activation Import</b></summary>

The application accepts full anatomical identifiers or standard sEMG acronyms interchangeably:

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

*(You can also use `"mvc"` instead of `"cmv"` in key names).*

</details>

---

## 🔧 Repository Structure

| File / Folder | Purpose |
| :--- | :--- |
| **`index.html`** | Standalone production web application (styles, logic, vector atlas, and brand assets inlined). |
| **`CITATION.cff`** | Citation File Format specification for automated academic citations on GitHub and Zenodo. |
| **`LICENSE`** | MIT License for application source code. |
| **`NOTICE.md`** | Comprehensive attribution notice, BodyParts3D origins, and figure reuse guidelines. |
| **`docs/screenshots/`** | Official screenshots for documentation and scientific presentations. |
| **`.github/workflows/deploy.yml`** | Automated continuous deployment workflow to GitHub Pages. |

---

## 📜 How to Cite & Academic License

If you use Muscle Map figures or activation maps in a scientific publication, thesis, or report, please cite both this repository and the underlying anatomical database:

### APA Style
> Panchairi, J. (2026). *Muscle Map: Interactive 2D vector anatomical atlas for surface electromyography (sEMG)* (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.24146734

### BibTeX
```bibtex
@software{panchairi2026musclemap,
  author       = {Panchairi, Jean},
  title        = {{Muscle Map: Interactive 2D vector anatomical atlas for surface electromyography (sEMG)}},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.24146734},
  url          = {https://technosport.github.io/Muscle-Map/}
}
```

### Anatomical Database Citation
> Mitsuhashi, N., Fujieda, K., Tamura, T., Kawamoto, S., Takagi, T., & Okubo, K. (2009). *BodyParts3D: 3D structure database for anatomical concepts*. **Nucleic Acids Research**, 37(suppl_1), D782–D785. https://doi.org/10.1093/nar/gkn613

### License Summary
- **Source Code**: Released under the **[MIT License](LICENSE)**.
- **Anatomical Vector Data & Exported Figures**: Released under **[CC BY-SA 2.1 JP](https://creativecommons.org/licenses/by-sa/2.1/jp/)**, derived from [BodyParts3D](https://lifesciencedb.jp/bp3d/) (DBCLS). Full details and commercial / publication rules in **[NOTICE.md](NOTICE.md)**.
