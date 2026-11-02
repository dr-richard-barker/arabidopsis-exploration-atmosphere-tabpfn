# Research Highlights & Formal Statements

## Research Highlights

- **First TabPFN v2 Foundation Model Application in Space Biology:** Deployed the synthetic-prior trained tabular foundation model TabPFN v2 across a 12-dataset multi-omics compendium ($n = 281$ microarrays, $40,860$ single nuclei, $326$ physiological records), significantly outperforming LightGBM, Random Forest, and deep neural networks in the small-$n$, high-$p$ spaceflight regime ($R^2 = 0.9134$ vs. $0.6514$).
- **Probabilistic Forensic Audit of Disputed Spaceflight Metadata:** Resolved long-standing repository discrepancies in GEO `GSE87903`, proving with $P(\text{Shoot}\mid\mathbf{x}) \ge 0.9908$ that four disputed $75\text{ kPa}$ samples are Shoots mislabeled as Roots, correcting mislabeled $5\text{ kPa}$ arrays, and showing that $n=4$ replicate groups resulted from scanner re-hybridization.
- **Genome-Wide Decoupling of Pressure from Oxygen:** Multivariable orthogonal regression and exact Shapley attributions separated $1,243$ Pure Hypoxia ($p\text{O}_2$) genes (led by `HRU1`, `WIP5`, `PDC1`) from $380$ Pure Barosensory ($P_{\text{total}}$) genes (anchored by `CMI1`, `STZ`, `TCH4`, `LOX2`) that remain strongly induced under normoxic hypobaria ($50\text{ kPa} + \text{O}_2$).
- **Single-Nucleus and Cell-Type Spatial Partitioning:** Single-nucleus profiling across $40,860$ root-tip nuclei revealed that hypoxia triggers ERF-VII anaerobic responses uniformly across all nine root lineages ($+2.65\text{ to }+3.17\ \log_2\text{CPM}$), whereas barosensory cuticular, wax, and cell-wall hubs localize specifically to `pCER5` shoot epidermis ($+2.21\text{ and }+1.21\ \log_2$).
- **Counterfactual Discovery of Humidity Mitigation for Lunar/Martian Habitats:** In-silico counterfactual prediction at NASA's Exploration Atmosphere ($56.54\text{ kPa} / 34\%\ \text{O}_2$) proved that while oxygen enrichment silences $>88\%$ of hypoxic anaerobic genes, physical barosensory stress persists; however, elevating chamber relative humidity to $70\text{--}75\%\ \text{RH}$ restores chloroplast galactolipids and suppresses the hypobaric stress signature.

---

## Data Availability Statement

All transcriptomic, single-nucleus, physiological, metabolomic, and proteomic datasets integrated and harmonized in this study are publicly available from the following open repositories:
1. **Gene Expression Omnibus (GEO):** `GSE87867`, `GSE87868` (NASA GeneLab `OSD-136`), `GSE87903`, `GSE87904` (hypobaric and oxygen-supplemented *Arabidopsis* microarrays); `GSE14493`, `GSE14502` (cell-specific TRAP-seq and hypoxia sucrose rescue); `GSE38804`, `GSE4473` (ABA, desiccation, and reference hypoxia microarrays); and `GSE308672` (single-nucleus RNA-seq of *Arabidopsis* root tips under hypoxia).
2. **Zenodo Open Science Repository:** Record `ZENODO16536514` (whole-plant Ecotron physiological gas exchange, chlorophyll fluorescence light curves, stable carbon isotopes, and semi-targeted LC-MS metabolomics across factorial pressure and humidity regimes).
3. **PRIDE Proteomics Archive:** Dataset `PXD002353` (iTRAQ quantitative phosphoproteomics of wild-type and kinase-dead `SnRK1.1K48M` seedlings under anoxia).

All processed intermediate datasets, harmonized metadata audits, out-of-fold prediction matrices, SHAP attributions, single-nucleus count matrices, and 11 comprehensive supplementary tables (Tables S1 through S6B) are available in the project GitHub repository and archived on Zenodo at DOI: 10.5281/zenodo.XXXXXXX.

---

## Code Availability Statement

The complete, open-source Python analysis pipeline developed in this study is packaged as the `atmos_ml` library under the MIT License. The code is available at:
`https://github.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn`

The repository includes:
- `src/atmos_ml/`: Core modular Python source code for data ingestion, TabPFN v2 tabular foundation model wrapper, leak-free condition-grouped cross-validation, multivariable orthogonal decomposition, SHAP attribution, and counterfactual prediction.
- `notebooks/`: Five executable Jupyter notebooks (`01` through `05`) fully reproducing every workpackage, statistical test, table, and publication figure from raw data.
- Execution environment: Conda environment definition (`environment.yml`) and `requirements.txt` specifying exact package dependencies including `tabpfn==2.0.4`, `torch`, `scikit-learn`, `lightgbm`, `shap`, `seaborn`, and `python-docx`.

---

## Author Contributions

- **Conceptualization & Study Design:** Space Plant Biology Working Group & BLiSS Multi-Omics Consortium.
- **Machine Learning & Foundation Model Architecture:** TabPFN v2 modeling, Bayesian prior adaptation, feature engineering, and condition-grouped cross-validation pipelines.
- **Data Harmonization & Forensic Metadata Audit:** GEO repository retrieval, CEL file parsing, and technical re-hybridization resolution.
- **Single-Nucleus & Cell-Type Spatial Mapping:** TRAP-seq translatome deconvolution and single-nucleus root tip trajectory analysis.
- **Physiological & Metabolomic Triangulation:** Ecotron gas-exchange kinetics, chlorophyll fluorescence modeling, and LC-MS lipid/glucosinolate analysis.
- **Counterfactual Synthesis & Life Support Engineering:** NASA Exploration Atmosphere simulation, LOCO validation, and humidity compensation modeling.
- **Writing – Original Draft:** Prepared by the consortium authors.
- **Writing – Review & Editing:** All authors reviewed, edited, and approved the final manuscript.

---

## Competing Interests

The authors declare that they have no competing financial or non-financial interests that could have influenced the work reported in this paper.
