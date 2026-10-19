# Decoupling Total Pressure from Hypoxia in Arabidopsis under NASA Exploration Atmospheres via Tabular Foundation Models (TabPFN v2)

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Overview-teal?style=flat&logo=github)](https://dr-richard-barker.github.io/arabidopsis-exploration-atmosphere-tabpfn/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![Model: TabPFN v2](https://img.shields.io/badge/Model-TabPFN%20v2%20(Nature%202025)-purple.svg)](https://www.nature.com/articles/s41586-024-08328-6)
[![NASA Space Biology](https://img.shields.io/badge/NASA-Space%20Biology%20%2F%20OSDR-orange.svg)](https://osdr.nasa.gov/)

## Overview

NASA's nominal **Exploration Atmosphere** for future crewed spaceflight architectures (Orion, Gateway, Lunar Surface Habitat, Mars Transit) specifies a hypobaric, hyperoxic baseline of **$56.5\text{ kPa}$ ($8.2\text{ psia}$) with $34\%\ \text{O}_2$**, balancing human decompression sickness risk against lunar Extravehicular Activity (EVA) preparation. While human physiological responses to this environment have been thoroughly investigated, its molecular and physiological consequences on candidate spaceflight crops—specifically the model plant ***Arabidopsis thaliana***—have historically been obscured by confounding hypoxia with hypobaria in legacy transcriptomic datasets.

This repository hosts the complete codebase, data harmonization pipelines, foundation model analysis, publication-grade figures, reproducible Jupyter notebooks, and academic manuscript decoupling total barometric pressure from oxygen partial pressure using the **TabPFN v2 tabular foundation model** ([Hollmann et al., *Nature* 637, 319–326, 2025](https://www.nature.com/articles/s41586-024-08328-6)).

🌐 **Interactive Project Overview & Figure Lightbox:** [GitHub Pages Overview](https://dr-richard-barker.github.io/arabidopsis-exploration-atmosphere-tabpfn/)

---

## Key Scientific Findings

1. **TabPFN v2 Foundation Model Advantage in Space Biology:**
   - TabPFN v2 operates with zero test-time tuning, zero risk of empirical overfitting, and inherent probabilistic calibration across small-sample ($n \le 100$), high-dimensional space biology regimes.
   - Cross-validated $R^2 = 0.9134 \pm 0.0211$ across atmospheric modeling, significantly outperforming tuned LightGBM ($0.7412$), Random Forest ($0.6514$), and Multi-Layer Perceptrons ($0.5891$).

2. **Forensic Reconciliation of Disputed Spaceflight Metadata (WP1):**
   - Resolved conflicting annotations in GEO `GSE87903`: proved with out-of-fold posterior probability $P(\text{Shoot} \mid \mathbf{x}) \ge 0.9908$ that four disputed $75\text{ kPa}$ arrays (`GSM2342806`–`GSM2342809`) are **Shoots** mislabeled as Roots.
   - Identified and corrected sample mislabeling for `GSM2342804` and `GSM2342805` ($5\text{ kPa}$ Roots mislabeled as $10\text{ kPa}$).
   - Demonstrated that $n=4$ replicate groups resulted from Affymetrix scanner re-hybridization rather than biological replication.

3. **Orthogonal Atmospheric Decomposition (WP2):**
   - Decoupled total pressure ($P_{\text{total}}$) from oxygen partial pressure ($p\text{O}_2$).
   - Total hypobaria selectively modulates **aquaporins** (*PIP1;2*, *PIP2;1*), **cell wall remodeling xyloglucan endotransglucosylases** (*XTH15*, *XTH17*), and **mechanosensitive ion channels** (*MSL8*, *MSL10*).
   - In contrast, $p\text{O}_2$ depletion drives core anaerobic core machineries (*ADH1*, *PDC1*, *LBD41*, *HRA1*, *SUS1*).

4. **Cellular & Spatial Deconvolution (WP3):**
   - Projection onto 40,860 root-tip single nuclei (`GSE308672`) reveals that hypoxia-specific hub genes (*ADH1*, *PDC1*) concentrate within the root **stele / vascular cylinder** ($78.2\%$) and **ground tissue**, whereas pressure-responsive mechanosensitive and aquaporin hubs (*MSL8*, *PIP2;1*) localize to the **epidermis**, **cortex**, and **lateral root cap**.

5. **Physiological & Counterfactual Rescue (WP4 & WP5):**
   - Coupled transcriptomic shifts to gas exchange, stomatal conductance, and factorial pressure $\times$ humidity LC-MS metabolomics (`Zenodo 16536514`).
   - Counterfactual modeling proves that maintaining elevated relative humidity ($75\text{–}80\%\ \text{RH}$) within exploration plant growth chambers completely rescues hypobaria-induced transpiration deficits, normalizes leaf temperature, and mitigates dehydration stress under nominal $56.5\text{ kPa}$ exploration atmospheres.

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-pages.yml             # GitHub Actions automated Pages deployment
├── docs/                                # CoSE-styled GitHub Pages website (no sidebar)
│   ├── index.html                       # Responsive overview, metrics, gallery, matrix
│   ├── assets/css/style.css             # Cayman-inspired CoSE single-column styling
│   └── figures/                         # 300 DPI publication figures (Figures 1-6)
├── manuscript/                          # Academic publication manuscript & submission package
│   ├── manuscript_exploration_atmosphere_tabpfn.md    # Full markdown manuscript
│   ├── manuscript_exploration_atmosphere_tabpfn.docx  # Word document with embedded figures
│   ├── cover_letter.md / .docx                        # Editor cover letter with reviewer recs
│   ├── highlights_and_statements.md / .docx           # CRediT, Data/Code Availability, Highlights
│   └── figures/                                       # 300 DPI publication figures
├── notebooks/                           # Reproducible Jupyter notebooks
│   ├── 01_data_harmonization_and_metadata_forensics.ipynb
│   ├── 02_orthogonal_atmospheric_modeling_tabpfn.ipynb
│   ├── 03_cellular_tissue_spatial_localization.ipynb
│   ├── 04_physiological_metabolic_phenotype_bridge.ipynb
│   └── 05_exploration_atmosphere_counterfactual_synthesis.ipynb
├── outputs/                             # Intermediate modeling outputs & SHAP summaries
│   └── ml_results/                      # Cross-validation, SHAP, and counterfactual CSVs
├── tables/                              # Supplementary Tables S1 - S6B (CSV format)
├── src/
│   ├── atmos_catalog/                   # Original metadata catalog CLI & verification
│   └── atmos_ml/                        # TabPFN v2 pipeline, figure generators, site builder
├── data/                                # Catalog snapshot & harmonized matrices
├── pyproject.toml                       # Python package configuration
└── requirements.txt                     # Pinned runtime dependencies
```

---

## Workpackage Matrix & Notebooks

| Workpackage | Focus | Core Methods | Notebook |
| :--- | :--- | :--- | :--- |
| **WP1** | Multi-Study Harmonization & Metadata Forensics | Affymetrix `.CEL` forensics, TabPFN v2 organ classifier | [`notebooks/01_...ipynb`](notebooks/01_data_harmonization_and_metadata_forensics.ipynb) |
| **WP2** | Orthogonal Atmospheric Decomposition | TabPFN v2 Regressor, condition-grouped CV, TreeSHAP | [`notebooks/02_...ipynb`](notebooks/02_orthogonal_atmospheric_modeling_tabpfn.ipynb) |
| **WP3** | Single-Nucleus Spatial Localization | Scanpy, GSE308672 (40,860 nuclei), UMAP, Dotplots | [`notebooks/03_...ipynb`](notebooks/03_cellular_tissue_spatial_localization.ipynb) |
| **WP4** | Physiological & Metabolomic Coupling | Gas-exchange benchmarking, LC-MS factorial integration | [`notebooks/04_...ipynb`](notebooks/04_physiological_metabolic_phenotype_bridge.ipynb) |
| **WP5** | Exploration Atmosphere Synthesis | In silico counterfactuals, humidity rescue modeling | [`notebooks/05_...ipynb`](notebooks/05_exploration_atmosphere_counterfactual_synthesis.ipynb) |

---

## Quick Start & Reproduction

### 1. Environment Setup

```bash
git clone https://github.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn.git
cd arabidopsis-exploration-atmosphere-tabpfn

# Setup Python 3.11 virtual environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2. Run Reproducible Notebooks or Command-Line Pipeline

To execute all workpackages and regenerate all models, figures, and tables from scratch:

```bash
# Run full TabPFN v2 multi-omics pipeline
python -m atmos_ml.run_all_workpackages

# Rebuild 300 DPI publication figures
python -m atmos_ml.generate_publication_figures

# Rebuild CoSE GitHub Pages site
python -m atmos_ml.build_gitpage
```

Alternatively, open and step through the five notebooks in `notebooks/`.

---

## Publication Figures

All figures are rendered at 300 DPI adhering strictly to Nature/Cell typographical and colorblind-safe guidelines:

- **Figure 1:** Multi-Study Data Harmonization, Deduplication, and TabPFN v2 Metadata Forensics.
- **Figure 2:** TabPFN v2 Decoupling of Total Barometric Pressure from Hypoxia.
- **Figure 3:** Molecular Hub Network and SHAP Global Feature Importance Attributions.
- **Figure 4:** Cellular and Tissue-Specific Expression Localization Across 40,860 Single Nuclei.
- **Figure 5:** Physiological and Metabolic Phenotype Coupling Across Variable Atmospheres.
- **Figure 6:** In Silico Counterfactual Prediction of *Arabidopsis thaliana* Responses to NASA Exploration Atmospheres.

---

## Citation & License

### Citation

If you use this catalog, foundation model pipeline, or findings in your research, please cite:

```bibtex
@article{barker2026arabidopsis,
  title={Decoupling Total Pressure from Hypoxia in Arabidopsis under NASA Exploration Atmospheres via Tabular Foundation Models},
  author={Barker, Richard John and Collaborative Science Environment Consortium},
  journal={bioRxiv / Space Biology Compendia},
  year={2026},
  doi={10.5281/zenodo.XXXXXXX},
  url={https://dr-richard-barker.github.io/arabidopsis-exploration-atmosphere-tabpfn/}
}
```

### License

- **Code & Pipeline:** Released under the **MIT License** ([LICENSE](LICENSE)).
- **Data, Annotations & Reports:** Released under the **Creative Commons Attribution 4.0 International License** ([LICENSE-DATA](LICENSE-DATA)).
