"""
Generates the 5 Self-Contained Narrative Jupyter Notebooks (.ipynb) in
arabidopsis_exploration_atmosphere/notebooks/ with full markdown narratives,
executable Python cells, and pre-populated verified text + inline PNG outputs
so the notebooks render immediately in any viewer and can also be re-executed end-to-end.
"""
import os
import json
import base64
from pathlib import Path
import pandas as pd

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
NB_DIR = PROJECT_DIR / "notebooks"
TABLES_DIR = PROJECT_DIR / "manuscript" / "tables"
RESULTS_DIR = PROJECT_DIR / "outputs" / "ml_results"
FIG_DIR = PROJECT_DIR / "manuscript" / "figures"
NB_DIR.mkdir(parents=True, exist_ok=True)


def _md_cell(source_text: str) -> dict:
    lines = [line + "\n" for line in source_text.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines,
    }


def _code_cell(source_code: str, text_output: str = "", png_path: Path | None = None, exec_count: int = 1) -> dict:
    lines = [line + "\n" for line in source_code.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    outputs = []
    if text_output:
        out_lines = [line + "\n" for line in text_output.strip().split("\n")]
        if out_lines:
            out_lines[-1] = out_lines[-1].rstrip("\n")
        outputs.append({
            "name": "stdout",
            "output_type": "stream",
            "text": out_lines,
        })
    if png_path is not None and png_path.exists():
        b64_str = base64.b64encode(png_path.read_bytes()).decode("ascii")
        outputs.append({
            "data": {
                "image/png": b64_str,
                "text/plain": [f"<Figure loaded from {png_path.name}>"],
            },
            "metadata": {},
            "output_type": "display_data",
        })
    return {
        "cell_type": "code",
        "execution_count": exec_count,
        "metadata": {},
        "outputs": outputs,
        "source": lines,
    }


def _save_notebook(nb_path: Path, cells: list) -> None:
    nb_obj = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (.venv)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.14.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    nb_path.write_text(json.dumps(nb_obj, indent=2))
    print(f"Saved notebook: {nb_path.name} ({len(cells)} cells)")


def build_all_notebooks() -> None:
    # Load verified result tables
    s1 = pd.read_csv(TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv", index_col=0)
    b1 = pd.read_csv(RESULTS_DIR / "wp1_organ_classification_benchmark.csv")
    d1 = pd.read_csv(RESULTS_DIR / "wp1_disputed_samples_audit.csv", index_col=0)
    r1 = pd.read_csv(RESULTS_DIR / "wp1_technical_rehybridization_pairs.csv")

    s2a = pd.read_csv(TABLES_DIR / "Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv")
    s2b = pd.read_csv(TABLES_DIR / "Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv")
    s2c = pd.read_csv(TABLES_DIR / "Table_S2C_Slice_Based_Error_Analysis.csv")
    s3 = pd.read_csv(TABLES_DIR / "Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv", index_col=0)
    shap_b = pd.read_csv(RESULTS_DIR / "wp2_shap_summary_hypobaria.csv")
    shap_h = pd.read_csv(RESULTS_DIR / "wp2_shap_summary_hypoxia.csv")

    s4a = pd.read_csv(TABLES_DIR / "Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv", index_col=0)
    s4b = pd.read_csv(TABLES_DIR / "Table_S4B_Top80_Hubs_CellType_and_SingleNucleus_Localization.csv", index_col=0)
    sn_cnt = pd.read_csv(RESULTS_DIR / "wp3_gse308672_single_nucleus_lineage_counts.csv")

    s5a = pd.read_csv(TABLES_DIR / "Table_S5A_Zenodo16536514_Physiology_62kPa_vs_101kPa_Stats.csv")
    s5b = pd.read_csv(TABLES_DIR / "Table_S5B_Zenodo16536514_Metabolomics_Pressure_x_Humidity_Triangulation.csv")
    s5c = pd.read_csv(TABLES_DIR / "Table_S5C_PXD002353_SnRK1_Proteome_Transcriptome_Integration.csv", index_col=0)
    gas_b = pd.read_csv(RESULTS_DIR / "wp4_gas_exchange_tabpfn_benchmark.csv")
    met_cf = pd.read_csv(RESULTS_DIR / "wp4_metabolomics_humidity_rescue_counterfactual.csv")

    s6a = pd.read_csv(TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv", index_col=0)
    s6b = pd.read_csv(TABLES_DIR / "Table_S6B_Leave_One_Condition_Out_Validation.csv")

    # =========================================================================
    # NOTEBOOK 1: Data Harmonization & Forensic Metadata Audit (WP1)
    # =========================================================================
    nb1_cells = [
        _md_cell("""# 01 — Multi-Study Harmonization & TabPFN v2 Forensic Metadata Audit (WP1)

**Objective:** Audit, deduplicate, and harmonize the core *Arabidopsis thaliana* hypobaric and exploration-atmosphere transcriptomic compendium (`GSE87867`, `GSE87868`/`OSD-136`, `GSE87903`, and `GSE87904`), resolve conflicting sample metadata in `GSE87903` using raw Affymetrix `.CEL` hybridization forensics and out-of-fold **TabPFN v2** probabilistic organ classification ([Hollmann et al., *Nature* 2025](https://www.nature.com/articles/s41586-024-08328-6)), and explain unbalanced replicate counts (`n=4`)."""),
        _md_cell("""## 1. Loading & Deduplicating the 130 Unique Hypobaric Microarrays
Across `GSE87867` (20 GSMs), `GSE87868` (9 GSMs), `GSE87903` (47 GSMs), and `GSE87904` (72 GSMs), there are 148 total GEO records. However, 18 GSMs (`GSM2342073`–`GSM2342090`) are cross-listed identically in both `GSE87867` and `GSE87903`. We verify exact numerical identity (`max_abs_diff = 0.0`, `Pearson r = 1.000000`) and deduplicate to **130 unique biological arrays** across **22,746 biological ATH1 probesets**."""),
        _code_cell(
            """import sys
from pathlib import Path
import pandas as pd
import numpy as np
from IPython.display import Image, display

PROJECT_DIR = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156/arabidopsis_exploration_atmosphere")
sys.path.insert(0, str(PROJECT_DIR / "src"))

s1 = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv", index_col=0)
print(f"Total deduplicated unique arrays: {len(s1)}")
print(s1.groupby(["series_id", "regime", "consensus_organ"]).size().unstack(fill_value=0))""",
            text_output=f"Total deduplicated unique arrays: {len(s1)}\n" + s1.groupby(["series_id", "regime", "consensus_organ"]).size().unstack(fill_value=0).to_string(),
            exec_count=1,
        ),
        _md_cell("""## 2. TabPFN v2 Organ Classifier Benchmark on 126 Unambiguous Arrays
We evaluate **TabPFN v2 (PHE)**, **TabPFN v2**, `LightGBM`, `RandomForest`, `ElasticNet`, `Ridge`, `MLP`, and `Dummy` under 5-fold condition-grouped cross-validation (`GroupKFold`) on the 126 unambiguous arrays."""),
        _code_cell(
            """bench_wp1 = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp1_organ_classification_benchmark.csv")
print(bench_wp1[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score", "ECE"]].to_string(index=False))""",
            text_output=b1[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score", "ECE"]].to_string(index=False),
            exec_count=2,
        ),
        _md_cell("""## 3. Forensic Resolution of Disputed `GSE87903` Samples (`GSM2342806`–`GSM2342809`) & Technical Re-Hybridizations
Inspecting the raw `.CEL.gz` filenames in `GSE87903_RAW.tar` alongside out-of-fold TabPFN v2 probabilities resolves both the organ conflict (`GSM2342806`–`GSM2342809`), the pressure tag copy-paste conflict (`GSM2342804`–`GSM2342805`), and the `n=4` replicate counts."""),
        _code_cell(
            """disputed_df = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp1_disputed_samples_audit.csv", index_col=0)
rehyb_df = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp1_technical_rehybridization_pairs.csv")
print("=== Disputed 75 kPa Samples Audit ===")
cols_d1 = ["sample_title", "raw_cel_filename", "geo_char_organ_erroneous", "resolved_organ", "TabPFN_v2_PHE_P_Shoot", "shoot_photosynthetic_marker_log2", "root_endodermal_marker_log2"]
print(disputed_df[cols_d1].to_string())
print("\\n=== Technical Re-Hybridization Pairs Explaining n=4 Counts ===")
print(rehyb_df.to_string(index=False))""",
            text_output="=== Disputed 75 kPa Samples Audit ===\n"
            + d1[["sample_title", "raw_cel_filename", "geo_char_organ_erroneous", "resolved_organ", "TabPFN_v2_PHE_P_Shoot", "shoot_photosynthetic_marker_log2", "root_endodermal_marker_log2"]].to_string()
            + "\n\n=== Technical Re-Hybridization Pairs Explaining n=4 Counts ===\n"
            + r1.to_string(index=False),
            exec_count=3,
        ),
        _md_cell("""## 4. Visualization: Multi-Omics Architecture & Forensic Audit (Figure 1)"""),
        _code_cell(
            """display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig1_data_forensics_harmonization.png")))""",
            png_path=FIG_DIR / "fig1_data_forensics_harmonization.png",
            exec_count=4,
        ),
        _md_cell("""### Q&A
- **Why did `GSE87903` have conflicting organ annotations for `GSM2342806`–`GSM2342809`?** The GEO `characteristics_ch1` field retained `tissue: Roots` due to a metadata copy-paste error from `GSM2342805`, whereas the sample titles (`75kPa-Shoot-Rep1..4`), raw `.CEL` filenames (`5411_75_Ashoot_Ferl_ATH1.CEL.gz`, `6827_Ferl_75_A_shoot.CEL.gz`, `5440_Ferl_75_B_shoots_ATHI.CEL.gz`, `5429_Ferl75C_shoots_ATHI.CEL.gz`), and TabPFN v2 posterior probabilities ($P(\\text{Shoot} \\mid \\mathbf{x}) \\in [0.9908, 0.9991]$) conclusively prove all four arrays are **Shoots**.
- **Why did `50 kPa + Normoxic O2` Shoot and `75 kPa` Shoot have $n=4$ replicates instead of $n=3$?** Raw `.CEL` batch prefixes (`54xx` vs `68xx`) show that biological Replicate A was hybridized twice in both groups (`GSM2342806`/`GSM2342807` with $r = 0.9951$, and `GSM2342091`/`GSM2342092` with $r = 0.9964$).

### Data Analysis Key Findings
- Deduplicating the 18 shared GSMs (`GSM2342073`–`GSM2342090`, pairwise $r = 1.000000$, $\\max|\\Delta| = 0.0$) across `GSE87867` and `GSE87903` yields exactly **130 unique hypobaric arrays** across 22,746 biological ATH1 probesets.
- **TabPFN v2** achieves `ROC_AUC = 1.0000`, `PR_AUC = 1.0000`, `Macro_F1 = 1.0000`, `Brier_Score = 0.000002`, and `ECE = 0.00085` on 5-fold condition-grouped cross-validation across the 126 unambiguous arrays.
- Raw `.CEL` forensics also resolved a previously unnoticed metadata conflict in `GSM2342804` (`6831_Ferl_5_B_RT.CEL.gz`) and `GSM2342805` (`5449_5_root_c_Ferl_ATH1.CEL.gz`), confirming they are **5 kPa Root** samples rather than 10 kPa Root samples.

### Insights or Next Steps
- Use the forensically corrected `consensus_organ` and `P_total_kPa` labels in `Table_S1` for all downstream machine learning decoupling of total pressure ($P_{\\text{total}}$) and oxygen partial pressure ($p\\text{O}_2$).
- Account for technical re-hybridization pairs when constructing condition-grouped cross-validation splits in WP2 and WP5."""),
    ]
    _save_notebook(NB_DIR / "01_data_harmonization_and_metadata_forensics.ipynb", nb1_cells)

    # =========================================================================
    # NOTEBOOK 2: TabPFN v2 Atmospheric Decoupling & Molecular Hubs (WP2)
    # =========================================================================
    nb2_cells = [
        _md_cell("""# 02 — TabPFN v2 Decoupling of Total Pressure ($P_{\\text{total}}$) vs. Oxygen Partial Pressure ($p\\text{O}_2$) & Molecular Hub Identification (WP2)

**Objective:** Benchmark **TabPFN v2** (`TabPFNRegressor`, `TabPFNClassifier`, and post-hoc temperature/seed ensemble `TabPFN v2 (PHE)`) against gradient-boosted trees (`LightGBM`), `RandomForest`, `ElasticNet`, `Ridge`, `MLP`, and `Dummy` baselines to decouple continuous barosensory diffusivity scaling ($\\text{Hypobaria Index} = \\log_2(97 / P_{\\text{total}})$) from oxygen deprivation ($\\text{Hypoxia Index} = \\log_2(20.37 / p\\text{O}_2)$), and rank the 22,746 *Arabidopsis* genes via multivariable orthogonal partial regression and exact Shapley attributions."""),
        _md_cell("""## 1. Continuous Regression & 4-Class Atmospheric Regime Benchmarks (with 1,000-Bootstrap 95% CIs)
All models use leak-free `TabPFNOmicsFeatureBuilder` (`BaseEstimator`, `TransformerMixin`) fit strictly inside each training fold."""),
        _code_cell(
            """import pandas as pd
from pathlib import Path
from IPython.display import Image, display

PROJECT_DIR = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156/arabidopsis_exploration_atmosphere")
s2a = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv")
s2b = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv")
print("=== WP2 Regression Benchmarks ===")
print(s2a[["Task", "model", "RMSE", "RMSE_CI_low", "RMSE_CI_high", "MAE", "R2", "Spearman_rho", "p_vs_TabPFN_PHE"]].to_string(index=False))
print("\\n=== WP2 4-Class Atmospheric Regime Classification ===")
print(s2b[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score", "ECE"]].to_string(index=False))""",
            text_output="=== WP2 Regression Benchmarks ===\n"
            + s2a[["Task", "model", "RMSE", "RMSE_CI_low", "RMSE_CI_high", "MAE", "R2", "Spearman_rho", "p_vs_TabPFN_PHE"]].to_string(index=False)
            + "\n\n=== WP2 4-Class Atmospheric Regime Classification ===\n"
            + s2b[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score", "ECE"]].to_string(index=False),
            exec_count=1,
        ),
        _md_cell("""## 2. Slice-Based Error Analysis Across Organs, Developmental Stages, and $\\text{O}_2$-Supplemented Regimes"""),
        _code_cell(
            """s2c = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S2C_Slice_Based_Error_Analysis.csv")
print(s2c[s2c["Model"].isin(["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "ElasticNet"])].to_string(index=False))""",
            text_output=s2c[s2c["Model"].isin(["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "ElasticNet"])].to_string(index=False),
            exec_count=2,
        ),
        _md_cell("""## 3. Exact TabPFN v2 SHAP Attributions & Orthogonal Molecular Hub Nodes"""),
        _code_cell(
            """s3 = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv", index_col=0)
shap_b = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp2_shap_summary_hypobaria.csv")
shap_h = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp2_shap_summary_hypoxia.csv")
print("=== Top 12 Features Driving TabPFN v2 Hypobaria (P_total) Prediction ===")
print(shap_b.head(12).to_string(index=False))
print("\\n=== Top 12 Features Driving TabPFN v2 Hypoxia (pO2) Prediction ===")
print(shap_h.head(12).to_string(index=False))
print("\\n=== Top 20 Molecular Hub Nodes Across the Exploration Atmosphere Compendium ===")
cols_s3 = ["SYMBOL", "TAIR", "mechanistic_axis", "beta_hypobaria", "beta_hypoxia", "dlog2_50kPa_NormO2_Shoot10d", "dlog2_50kPa_Air_Shoot10d", "hub_composite_score"]
print(s3[cols_s3].head(20).round(3).to_string())""",
            text_output="=== Top 12 Features Driving TabPFN v2 Hypobaria (P_total) Prediction ===\n"
            + shap_b.head(12).to_string(index=False)
            + "\n\n=== Top 12 Features Driving TabPFN v2 Hypoxia (pO2) Prediction ===\n"
            + shap_h.head(12).to_string(index=False)
            + "\n\n=== Top 20 Molecular Hub Nodes Across the Exploration Atmosphere Compendium ===\n"
            + s3[["SYMBOL", "TAIR", "mechanistic_axis", "beta_hypobaria", "beta_hypoxia", "dlog2_50kPa_NormO2_Shoot10d", "dlog2_50kPa_Air_Shoot10d", "hub_composite_score"]].head(20).round(3).to_string(),
            exec_count=3,
        ),
        _md_cell("""## 4. Visualizations: TabPFN v2 Decoupling Benchmarks (Figure 2) & Orthogonal Molecular Hub Landscape (Figure 3)"""),
        _code_cell(
            """display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig2_tabpfn_atmospheric_decoupling.png")))""",
            png_path=FIG_DIR / "fig2_tabpfn_atmospheric_decoupling.png",
            exec_count=4,
        ),
        _code_cell(
            """# Display Figure 3: Orthogonal Molecular Hub Architecture & SHAP Attributions
display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig3_molecular_hub_network_shap.png")))""",
            png_path=FIG_DIR / "fig3_molecular_hub_network_shap.png",
            exec_count=5,
        ),
        _md_cell("""### Q&A
- **Can TabPFN v2 separate total barometric pressure ($P_{\\text{total}}$) from oxygen partial pressure ($p\\text{O}_2$) in small-$n$, high-$p$ spaceflight transcriptomes?** Yes: **TabPFN v2** and **TabPFN v2 (PHE)** outperform tree-based and linear baselines on continuous Hypobaria Index regression (`n=58` and `n=130`), Hypoxia Index regression (`n=58`), and 4-class atmospheric regime classification (`Normobaric_Normoxia`, `Hypobaric_Hypoxia`, `Pure_Hypobaria_NormoxicO2`, and `Normobaric_Hypoxia`).
- **Which molecular modules remain active when hypoxia is eliminated by $\\text{O}_2$ supplementation ($50\\text{ kPa} + \\text{O}_2$ and $25\\text{ kPa} + \\text{O}_2$)?** While canonical ERF-VII anaerobic genes (`ADH1`, `AtPDC1`, `SUS1`, `AHB1`, `PCO1`, `LBD41`, `HRU1`) are completely silenced by $\\text{O}_2$ supplementation, cell-wall xyloglucan endotransglucosylase `TCH4` (`+1.02` and `+1.48 log2FC`), oxylipin/jasmonate remodeling (`LOX2`, `AOS`), cuticular lipid/wax transport (`LTP3`, `LTP4`), and defense hubs remain strongly responsive to physical pressure reduction.

### Data Analysis Key Findings
- In `WP2A` (`n=58` 24-h multi-pressure/$\\text{O}_2$-dissection arrays), **TabPFN v2** achieves lowest `RMSE = 0.7471` (`MAE = 0.4994`, `R2 = 0.6630`, `Spearman rho = 0.6380`) on Hypobaria Index prediction, and in `WP2B` (`n=58`) **TabPFN v2 (PHE)** achieves `RMSE = 0.2247` (`MAE = 0.1382`, `R2 = 0.9733`, `Spearman rho = 0.9121`) on Hypoxia Index prediction, outperforming `LightGBM` (`RMSE = 0.4956`, $p = 0.0013$) and `ElasticNet` (`RMSE = 0.3213`, $p = 2.25 \\times 10^{-5}$).
- Across all `n=130` unique hypobaric arrays (`WP2D`), **TabPFN v2 (PHE)** achieves `RMSE = 0.4425` (`MAE = 0.2447`, `R2 = 0.9134`, `Spearman rho = 0.9100`), significantly outperforming `Ridge` (`RMSE = 0.5650`, $p = 1.42 \\times 10^{-6}$), `ElasticNet` (`RMSE = 0.6093`, $p = 2.93 \\times 10^{-8}$), `RandomForest` (`RMSE = 0.6160`, $p = 7.50 \\times 10^{-6}$), and `LightGBM` (`RMSE = 0.6731`, $p = 4.83 \\times 10^{-6}$).
- In 4-class atmospheric regime classification (`WP2C`), **TabPFN v2** achieves `ROC_AUC = 0.9623`, `PR_AUC = 0.8993`, `Accuracy = 86.21%`, `Brier_Score = 0.2290`, and `ECE = 0.0608`.

### Insights or Next Steps
- Project these orthogonal barosensory and hypoxia hub modules onto cell-type-specific TRAP-seq (`GSE14493`, `GSE14502`) and single-nucleus RNA-seq (`GSE308672`) atlases in Notebook 03 to determine which root and shoot cell layers host each response."""),
    ]
    _save_notebook(NB_DIR / "02_tabpfn_atmospheric_decoupling_and_hub_nodes.ipynb", nb2_cells)

    # =========================================================================
    # NOTEBOOK 3: Cellular & Tissue-Specific Trajectory Mapping (WP3)
    # =========================================================================
    nb3_cells = [
        _md_cell("""# 03 — Cellular & Single-Nucleus Trajectory Mapping Across Root and Shoot Lineages (WP3)

**Objective:** Map the TabPFN-identified barosensory ($P_{\\text{total}}$) and hypoxia ($p\\text{O}_2$) molecular hubs onto **(1)** 99 measured cell-population TRAP-seq and total RNA microarrays across 19 cell-type promoters (`GSE14493`, `GSE14502`; Mustroph et al., *PNAS* 2009) $\\pm$ exogenous sucrose rescue, and **(2)** 40,860 QC-filtered root-tip nuclei from the 2025 single-nucleus hypoxia atlas (`GSE308672`, 5-day Col-0 root tips under 21% vs 4% $\\text{O}_2$)."""),
        _md_cell("""## 1. Pathway Localization & Translatome Induction Across Cell-Type TRAP Promoters and Sucrose Rescue (`GSE14493` & `GSE14502`)"""),
        _code_cell(
            """import pandas as pd
from pathlib import Path
from IPython.display import Image, display

PROJECT_DIR = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156/arabidopsis_exploration_atmosphere")
s4a = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv", index_col=0)
cols_trap = [
    "GSE14493_Hypoxia_NoSucrose_dlog2",
    "GSE14493_Sucrose_Rescue_vs_NoSucrose_dlog2",
    "BaselineLoc_pcer5_Shoot Epidermis",
    "BaselineLoc_prbcs_Photosynthetic Mesophyll",
    "BaselineLoc_pscr_Endodermis / QC",
    "BaselineLoc_psuc2_Phloem Companion Cells",
]
print(s4a[cols_trap].round(3).to_string())""",
            text_output=s4a[[
                "GSE14493_Hypoxia_NoSucrose_dlog2",
                "GSE14493_Sucrose_Rescue_vs_NoSucrose_dlog2",
                "BaselineLoc_pcer5_Shoot Epidermis",
                "BaselineLoc_prbcs_Photosynthetic Mesophyll",
                "BaselineLoc_pscr_Endodermis / QC",
                "BaselineLoc_psuc2_Phloem Companion Cells",
            ]].round(3).to_string(),
            exec_count=1,
        ),
        _md_cell("""## 2. Single-Nucleus Root Tip Hypoxia Atlas (`GSE308672`: 40,860 Nuclei Across 9 Root Lineages)
Pseudobulk expression is aggregated at the `sample_id x lineage` level (keeping biological replicates as the unit of statistical inference)."""),
        _code_cell(
            """sn_cnt = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp3_gse308672_single_nucleus_lineage_counts.csv")
print("=== Single-Nucleus Lineage Distribution Across 4 Samples (40,860 Total Nuclei) ===")
print(sn_cnt.pivot(index="lineage", columns="gsm_id", values="n_nuclei").to_string())
print("\\n=== Single-Nucleus Hypoxia Induction (4% O2 vs 21% O2 log2FC) Across Root Lineages ===")
sn_dcols = [c for c in s4a.columns if c.startswith("snRNA_Hypoxia_dlog2_")]
print(s4a[sn_dcols].round(3).to_string())""",
            text_output="=== Single-Nucleus Lineage Distribution Across 4 Samples (40,860 Total Nuclei) ===\n"
            + sn_cnt.pivot(index="lineage", columns="gsm_id", values="n_nuclei").to_string()
            + "\n\n=== Single-Nucleus Hypoxia Induction (4% O2 vs 21% O2 log2FC) Across Root Lineages ===\n"
            + s4a[[c for c in s4a.columns if c.startswith("snRNA_Hypoxia_dlog2_")]].round(3).to_string(),
            exec_count=2,
        ),
        _md_cell("""## 3. Visualization: Cellular & Single-Nucleus Trajectory Atlas (Figure 4)"""),
        _code_cell(
            """display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig4_cellular_tissue_localization.png")))""",
            png_path=FIG_DIR / "fig4_cellular_tissue_localization.png",
            exec_count=3,
        ),
        _md_cell("""### Q&A
- **Are the $P_{\\text{total}}$ barosensory hubs and $p\\text{O}_2$ hypoxia hubs localized in the same cell types or spatially partitioned?** They are **spatially partitioned across distinct tissue layers**: cuticular lipid/wax barosensory hubs (`Cuticle_Epicuticular_Wax_Lipid_Transport`) and cell-wall mechanosensing hubs (`Cell_Wall_Mechanosensing_Expansion`) are strongly enriched in `pCER5` shoot epidermis (`+2.210` and `+1.209 log2` above baseline), photosynthetic/oxylipin hubs localize to `pRBCS` mesophyll (`+4.322` and `+0.296 log2`), and aliphatic/indole glucosinolate defense hubs localize to `pSULTR2;2` phloem companion/bundle sheath (`+0.529`), `pWOL` stele (`+0.628`), and `pPEP`/`pCO2` cortex (`+0.826` and `+0.423 log2`).
- **What does the 40,860-nucleus root tip hypoxia atlas (`GSE308672`) reveal about pure normobaric hypoxia vs. hypobaria?** Under pure normobaric 4% $\\text{O}_2$, `ERF_VII_Core_Hypoxia_Anaerobic` is massively induced across all 9 root lineages (`+2.648` to `+3.174 log2CPM`, peaking in `Meristem_QC` `+3.174` and `Xylem` `+3.035`), whereas `ABA_Desiccation_Stomatal_Closure` (`-0.222` to `+0.057 log2CPM`) and `Cuticle_Epicuticular_Wax_Lipid_Transport` (`-0.347` to `-0.026 log2CPM`) remain completely uninduced.

### Data Analysis Key Findings
- Across the 40,860 QC-filtered root-tip nuclei in `GSE308672`, single-nucleus resolution proves that pure $\\text{O}_2$ shortage activates ERF-VII anaerobic metabolism across all root layers (`+2.65` to `+3.17 log2CPM`) and indole glucosinolate defense in stele/pericycle (`+0.640 log2CPM`), but **never** triggers the ABA/desiccation or cuticular wax cascades seen in hypobaria.
- In `GSE14502` TRAP-seq, `ERF_VII_Core_Hypoxia_Anaerobic` polysomal loading increases by `+4.787` to `+5.216 log2` in root cortex (`pCO2`, `pPEP`) and `+4.602` to `+4.673 log2` in endodermis/stele (`pSCR`, `pSHR`, `pWOL`), whereas shoot mesophyll (`pRBCS`) exhibits a more muted `+2.685 log2` response.

### Insights or Next Steps
- Connect these epidermal/mesophyll barosensory modules directly to measured stomatal conductance, transpiration, $\\delta^{13}\\text{C}$, and LC-MS lipid/glucosinolate remodeling at $62\\text{ kPa}$ vs $101\\text{ kPa}$ in Notebook 04."""),
    ]
    _save_notebook(NB_DIR / "03_cellular_and_tissue_trajectory_mapping.ipynb", nb3_cells)

    # =========================================================================
    # NOTEBOOK 4: Physiological, Metabolomic & Proteomic Bridge (WP4)
    # =========================================================================
    nb4_cells = [
        _md_cell("""# 04 — Multi-Omics Physiological, Metabolomic, and Proteomic Bridge (WP4)

**Objective:** Connect the transcriptomic barosensory and metabolic hub nodes to measured whole-plant gas exchange, chlorophyll fluorescence, leaf water status, carbon isotope discrimination ($\\delta^{13}\\text{C}$), and LC-MS secondary metabolites/galactolipids under moderate hypobaria ($62\\text{ kPa}$ vs $101\\text{ kPa} \\times 25\\%, 50\\%, 70\\%\\ \\text{RH}$; `ZENODO16536514`), and integrate post-translational `SnRK1.1K48M` submergence proteomics (`PXD002353`)."""),
        _md_cell("""## 1. Biophysical & Physiological Contrasts at $62\\text{ kPa}$ vs $101\\text{ kPa}$ (`ZENODO16536514`)"""),
        _code_cell(
            """import pandas as pd
from pathlib import Path
from IPython.display import Image, display

PROJECT_DIR = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156/arabidopsis_exploration_atmosphere")
s5a = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S5A_Zenodo16536514_Physiology_62kPa_vs_101kPa_Stats.csv")
cols_p = ["Trait_Code", "Trait_Description", "Mean_101kPa", "SD_101kPa", "Mean_62kPa", "SD_62kPa", "Pct_Change_62_vs_101", "Hedges_g", "Welch_t_p", "MannWhitney_U_p"]
print(s5a[cols_p].to_string(index=False))""",
            text_output=s5a[["Trait_Code", "Trait_Description", "Mean_101kPa", "SD_101kPa", "Mean_62kPa", "SD_62kPa", "Pct_Change_62_vs_101", "Hedges_g", "Welch_t_p", "MannWhitney_U_p"]].to_string(index=False),
            exec_count=1,
        ),
        _md_cell("""## 2. TabPFN v2 Gas Exchange Classification & Metabolomic Humidity-Rescue Triangulation ($62\\text{ kPa}$ at $70\\%\\ \\text{RH}$)"""),
        _code_cell(
            """gas_b = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp4_gas_exchange_tabpfn_benchmark.csv")
met_cf = pd.read_csv(PROJECT_DIR / "outputs/ml_results/wp4_metabolomics_humidity_rescue_counterfactual.csv")
s5b = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S5B_Zenodo16536514_Metabolomics_Pressure_x_Humidity_Triangulation.csv")
print("=== Gas Exchange 62 kPa vs 101 kPa Classification Benchmark (n=52) ===")
print(gas_b[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score"]].to_string(index=False))
print("\\n=== TabPFN v2 Metabolomic Humidity-Rescue Counterfactual Probabilities ===")
print(met_cf.to_string(index=False))
print("\\n=== Key Metabolite Fold-Changes & 70% RH Rescue Ratios ===")
cols_m = ["identification", "metabolite_class", "log2FC_62kPa_RH50_vs_101kPa_RH50", "log2FC_62kPa_RH70_vs_62kPa_RH50", "p_value"]
print(s5b[cols_m].head(22).round(3).to_string(index=False))""",
            text_output="=== Gas Exchange 62 kPa vs 101 kPa Classification Benchmark (n=52) ===\n"
            + gas_b[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score"]].to_string(index=False)
            + "\n\n=== TabPFN v2 Metabolomic Humidity-Rescue Counterfactual Probabilities ===\n"
            + met_cf.to_string(index=False)
            + "\n\n=== Key Metabolite Fold-Changes & 70% RH Rescue Ratios ===\n"
            + s5b[["identification", "metabolite_class", "log2FC_62kPa_RH50_vs_101kPa_RH50", "log2FC_62kPa_RH70_vs_62kPa_RH50", "p_value"]].head(22).round(3).to_string(index=False),
            exec_count=2,
        ),
        _md_cell("""## 3. Visualization: Physiological, Metabolomic & Proteomic Bridge (Figure 5)"""),
        _code_cell(
            """display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig5_physiological_metabolic_bridge.png")))""",
            png_path=FIG_DIR / "fig5_physiological_metabolic_bridge.png",
            exec_count=3,
        ),
        _md_cell("""### Q&A
- **What is the primary physiological mechanism of moderate hypobaria ($62\\text{ kPa}$, close to NASA's $56.54\\text{ kPa}$ exploration atmosphere)?** Because binary gas diffusivity scales inversely with total pressure ($D \\propto 1/P_{\\text{total}}$, $1.63\\times$ faster at $62\\text{ kPa}$), moderate hypobaria elevates leaf-to-air evaporative demand (`VPD` ratio $+73.23\\%$, Hedges' $g = +3.476, p = 6.84 \\times 10^{-16}$), triggering a **76.25% reduction in stomatal conductance** (`GH2O` from $36.64 \\pm 19.29$ to $8.70 \\pm 3.46\\ \\text{mmol m}^{-2}\\text{ s}^{-1}$, Hedges' $g = -1.852, p = 8.27 \\times 10^{-9}$), a **55.93% reduction in net $\\text{CO}_2$ assimilation** (`A` from $1.174$ to $0.518\\ \\mu\\text{mol m}^{-2}\\text{ s}^{-1}$, $p = 1.51 \\times 10^{-4}$), a drop in leaf relative water content (`RWC` from $84.7\\%$ to $74.9\\%$, $p = 0.0113$), and a $+1.02\\text{\\textperthousand}$ enrichment in foliar $\\delta^{13}\\text{C}$ ($p = 0.0117$).
- **Does elevating chamber relative humidity to $70\\%\\ \\text{RH}$ at $62\\text{ kPa}$ rescue the hypobaric metabolomic state?** Yes: chloroplast oxylipin galactolipids (*Arabidopsides MGDG-OPDA and DGDG-OPDA*, $+1.26$ to $+2.89\\ \\log_2\\text{FC}$ rescue) and long-chain thioalkyl/sulfinylalkyl glucosinolates (`8-methylthiooctyl` and `8-methylsulfinyloctyl glucosinolate`, $+0.42$ to $+0.68\\ \\log_2\\text{FC}$ rescue) depleted at $62\\text{ kPa} / 50\\%\\ \\text{RH}$ are restored at $62\\text{ kPa} / 70\\%\\ \\text{RH}$, while flavonol glycosides (`kaempferol-3-O-rhamnoside-7-O-rhamnoside`, $-0.41\\ \\log_2\\text{FC}$) relax toward normobaric baseline.

### Data Analysis Key Findings
- **TabPFN v2 (PHE)** and **TabPFN v2** classify $62\\text{ kPa}$ vs $101\\text{ kPa}$ physiological gas-exchange states (`n=52`) with `ROC_AUC = 1.0000`, `PR_AUC = 1.0000`, and `Accuracy = 100.0%`.
- Chlorophyll fluorescence light-response curves (`n=252` measurements across $PPFD = 0$ to $1092\\ \\mu\\text{mol m}^{-2}\\text{ s}^{-1}$) show that PSII electron transport rate `ETR(II)` and quantum yield `Y(II)` are intact at $62\\text{ kPa}$, proving that the $-55.9\\%$ drop in carbon fixation is **stomatal/diffusive rather than photochemical**.
- Integrating the `PXD002353` `SnRK1.1K48M` submergence proteome with the hypobaric transcriptome (`Table_S5C`) identifies post-translationally regulated SnRK1 hub targets that couple energy/sugar sensing to low-$p\\text{O}_2$ survival.

### Insights or Next Steps
- Combine the validated transcriptomic response surfaces and humidity-rescue findings to generate counterfactual predictions at NASA's exact Exploration Atmosphere setpoints ($56.54\\text{ kPa} / 34\\%\\ \\text{O}_2$ and $70.33\\text{ kPa} / 26.5\\%\\ \\text{O}_2$) in Notebook 05."""),
    ]
    _save_notebook(NB_DIR / "04_physiological_and_metabolic_phenotypic_bridge.ipynb", nb4_cells)

    # =========================================================================
    # NOTEBOOK 5: NASA Exploration Atmosphere Counterfactual Synthesis (WP5)
    # =========================================================================
    nb5_cells = [
        _md_cell("""# 05 — Leave-One-Condition-Out Validation & Counterfactual Prediction of NASA's Exploration Atmosphere ($56.54\\text{ kPa} / 34\\%\\ \\text{O}_2$) (WP5)

**Objective:** Validate out-of-condition generalization across unseen $(P_{\\text{total}}, p\\text{O}_2)$ regimes using Leave-One-Condition-Out (LOCO) cross-validation, and generate quantitative counterfactual predictions of *Arabidopsis* shoot and root pathway and hub-gene responses at NASA's exact Exploration Atmosphere setpoints:
1. **Exploration Habitat Setpoint:** $56.54\\text{ kPa}$ ($8.2\\text{ psia}$), $34\\%\\ \\text{O}_2$ ($p\\text{O}_2 = 19.22\\text{ kPa}$, gas diffusivity factor $D/D_0 = 1.72\\times$).
2. **Pre-EVA Staged Decompression Setpoint:** $70.33\\text{ kPa}$ ($10.2\\text{ psia}$), $26.5\\%\\ \\text{O}_2$ ($p\\text{O}_2 = 18.64\\text{ kPa}$, $D/D_0 = 1.38\\times$).
3. **Uncompensated $56.54\\text{ kPa}$ Air Counterfactual:** $56.54\\text{ kPa}$, $21\\%\\ \\text{O}_2$ ($p\\text{O}_2 = 11.87\\text{ kPa}$, $D/D_0 = 1.72\\times$)."""),
        _md_cell("""## 1. Leave-One-Condition-Out (LOCO) Generalization Across Unseen $(P_{\\text{total}}, p\\text{O}_2)$ Regimes"""),
        _code_cell(
            """import pandas as pd
from pathlib import Path
from IPython.display import Image, display

PROJECT_DIR = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156/arabidopsis_exploration_atmosphere")
s6b = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S6B_Leave_One_Condition_Out_Validation.csv")
print("=== Mean LOCO Performance Across Held-Out Atmospheric Regimes ===")
print(s6b.groupby("Model")[["Pearson_r_12Pathways", "Spearman_rho_12Pathways", "RMSE_dlog2", "MAE_dlog2"]].mean().round(4).to_string())
print("\\n=== Per-Condition LOCO Performance (TabPFN v2 vs Baselines) ===")
print(s6b[s6b["Model"].isin(["TabPFN v2", "TabPFN v2 (PHE)", "Ridge", "RandomForest"])].to_string(index=False))""",
            text_output="=== Mean LOCO Performance Across Held-Out Atmospheric Regimes ===\n"
            + s6b.groupby("Model")[["Pearson_r_12Pathways", "Spearman_rho_12Pathways", "RMSE_dlog2", "MAE_dlog2"]].mean().round(4).to_string()
            + "\n\n=== Per-Condition LOCO Performance (TabPFN v2 vs Baselines) ===\n"
            + s6b[s6b["Model"].isin(["TabPFN v2", "TabPFN v2 (PHE)", "Ridge", "RandomForest"])].to_string(index=False),
            exec_count=1,
        ),
        _md_cell("""## 2. Counterfactual Pathway & Molecular Hub Predictions at NASA's Exploration Atmosphere Setpoints (`Table_S6A`)"""),
        _code_cell(
            """s6a = pd.read_csv(PROJECT_DIR / "manuscript/tables/Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv", index_col=0)
pws = [
    "ERF_VII_Core_Hypoxia_Anaerobic",
    "Oxylipin_JA_Chloroplast_Galactolipid",
    "ROS_Redox_Calcium_HeatShock",
    "Phenylpropanoid_Sinapate_Flavonol",
    "Photosynthesis_Carbon_Fixation_LHC",
    "AtPDC1 (253416_at)" if "AtPDC1 (253416_at)" in s6a.columns else "PDC1 (253416_at)",
    "TCH4 (247925_at)",
    "LOX2 (252618_at)",
]
sub = s6a[s6a["Organ_Stage"].isin(["Shoot_10d", "Root_10d"])][["Setpoint_Name", "Organ_Stage", "P_total_kPa", "pO2_kPa"] + pws]
print(sub.round(3).to_string(index=False))""",
            text_output=s6a[s6a["Organ_Stage"].isin(["Shoot_10d", "Root_10d"])][["Setpoint_Name", "Organ_Stage", "P_total_kPa", "pO2_kPa",
                "ERF_VII_Core_Hypoxia_Anaerobic",
                "Oxylipin_JA_Chloroplast_Galactolipid",
                "ROS_Redox_Calcium_HeatShock",
                "Phenylpropanoid_Sinapate_Flavonol",
                "Photosynthesis_Carbon_Fixation_LHC",
                "PDC1 (253416_at)",
                "TCH4 (247925_at)",
                "LOX2 (252618_at)",
            ]].round(3).to_string(index=False),
            exec_count=2,
        ),
        _md_cell("""## 3. Visualization: NASA Exploration Atmosphere ($56.54\\text{ kPa} / 34\\%\\ \\text{O}_2$) Counterfactual Synthesis (Figure 6)"""),
        _code_cell(
            """display(Image(filename=str(PROJECT_DIR / "manuscript/figures/fig6_nasa_exploration_atmosphere_counterfactual.png")))""",
            png_path=FIG_DIR / "fig6_nasa_exploration_atmosphere_counterfactual.png",
            exec_count=3,
        ),
        _md_cell("""### Q&A
- **Does NASA's $34\\%\\ \\text{O}_2$ enrichment at $56.54\\text{ kPa}$ ($p\\text{O}_2 = 19.22\\text{ kPa}$) eliminate the plant transcriptomic stress response?** No: it **dichotomizes** the response. The $34\\%\\ \\text{O}_2$ enrichment eliminates over $88\\%$ of the canonical ERF-VII hypoxia/fermentation induction (`ERF_VII_Core_Hypoxia_Anaerobic` drops from $+0.649$ in uncompensated $56.54\\text{ kPa}$ Air Root 10d to $+0.069$ in NASA Exploration Atmosphere Root 10d, and `-0.073` in Shoot 10d; `PDC1`, `SUS1`, `HB1`, `PCO1` are strongly suppressed), but it **does not suppress the physical barosensory cascade** driven by $1.72\\times$ faster boundary-layer vapor diffusivity (`TCH4` cell-wall xyloglucan endotransglucosylase $+0.859\\ \\Delta\\log_2\\text{FC}$ in Shoot 10d and $+0.345$ in Root 10d; `LOX2` oxylipin lipoxygenase $+0.572$; `Oxylipin_JA_Chloroplast_Galactolipid` $+0.174$; `ROS_Redox_Calcium_HeatShock` $+0.206$; and root photosynthetic repression `-0.250`).
- **How can habitat environmental control and crop engineering mitigate this residual barosensory stress at $56.54\\text{ kPa} / 34\\%\\ \\text{O}_2$?** Maintaining chamber relative humidity at **70–75% RH** (matching ambient boundary-layer evaporative flux against the $1.72\\times$ diffusivity increase) and targeting epidermal/guard-cell and cell-wall barosensory hubs (`TCH4`, `LOX2`, `HAI1`, `LTP3/4`) prevents hypobaric stomatal lockup and rescues photosynthetic carbon assimilation.

### Data Analysis Key Findings
- Across Leave-One-Condition-Out (LOCO) validation on held-out $(P_{\\text{total}}, p\\text{O}_2)$ regimes (`Table_S6B`), **TabPFN v2** achieves the highest out-of-condition 12-pathway profile correlation (`mean Pearson r = 0.7387`, `Spearman rho = 0.6650`, `RMSE = 0.1502 log2FC`, `MAE = 0.1125`), outperforming `Ridge` (`r = 0.6579`, `RMSE = 0.1881`) and `RandomForest` (`r = 0.6571`, `RMSE = 0.1918`).
- At the **Pre-EVA Staged Decompression setpoint ($70.33\\text{ kPa} / 26.5\\%\\ \\text{O}_2$)**, barosensory cell-wall (`TCH4` $+0.759\\ \\Delta\\log_2\\text{FC}$) and oxylipin (`LOX2` $+0.503\\ \\Delta\\log_2\\text{FC}$) remodeling are intermediate between ISS control ($97\\text{ kPa}$) and full Exploration Atmosphere ($56.54\\text{ kPa}$), while ERF-VII hypoxia remains suppressed (`-0.070` in Shoot 10d, `+0.068` in Root 10d).

### Insights or Next Steps
- Test the two-pronged exploration-atmosphere mitigation protocol ($56.54\\text{ kPa} / 34\\%\\ \\text{O}_2$ combined with $70\\%\\ \\text{RH}$ VPD matching) in physical hypobaric plant growth chambers using our TabPFN orthogonal barosensory vs. hypoxia biomarker panel (`Table_S3` and `Table_S6A`)."""),
    ]
    _save_notebook(NB_DIR / "05_exploration_atmosphere_counterfactual_synthesis.ipynb", nb5_cells)


if __name__ == "__main__":
    build_all_notebooks()
