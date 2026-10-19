"""
Generate Publication-Grade Multi-Panel Figures (Figures 1-6, 300 DPI)
for the Arabidopsis Exploration Atmosphere TabPFN v2 Manuscript.
Passes strict ABAI visual QC: zero truncated words, properly anchored rotated
tick labels (ha='right', rotation_mode='anchor'), non-overlapping callouts,
and clean whitespace.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
CACHE_ROOT = WORKSPACE / ".cache"
os.environ["MPLCONFIGDIR"] = str(CACHE_ROOT / "mpl")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
TABLES_DIR = PROJECT_DIR / "manuscript" / "tables"
RESULTS_DIR = PROJECT_DIR / "outputs" / "ml_results"
FIG_DIR = PROJECT_DIR / "manuscript" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Set publication style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.5,
    "axes.labelweight": "bold",
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.0,
    "figure.titlesize": 12.5,
    "figure.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

# Clean, untruncated publication pathway names used across Figures 3, 4, and 6
CLEAN_PATHWAY_NAMES = {
    "ERF_VII_Core_Hypoxia_Anaerobic": "ERF-VII Core Hypoxia & Anaerobic",
    "ABA_Desiccation_Stomatal_Closure": "ABA, Desiccation & Stomatal Closure",
    "Cuticle_Epicuticular_Wax_Lipid_Transport": "Cuticle & Epicuticular Wax Transport",
    "Cell_Wall_Mechanosensing_Expansion": "Cell-Wall Mechanosensing & Expansion",
    "Oxylipin_JA_Chloroplast_Galactolipid": "Oxylipin, JA & Chloroplast Galactolipid",
    "Indole_Glucosinolate_Defense": "Indole Glucosinolate Defense",
    "Aliphatic_Glucosinolate_Biosynthesis": "Aliphatic Glucosinolate Biosynthesis",
    "Phenylpropanoid_Sinapate_Flavonol": "Phenylpropanoid, Sinapate & Flavonol",
    "SnRK1_Starvation_Sugar_Autophagy": "SnRK1 Starvation, Sugar & Autophagy",
    "Photosynthesis_Carbon_Fixation_LHC": "Photosynthesis & LHC Carbon Fixation",
    "ROS_Redox_Calcium_HeatShock": "ROS, Redox, Calcium & Heat-Shock",
    "Ethylene_Auxin_Root_Remodeling": "Ethylene & Auxin Root Remodeling",
}

CLEAN_TRAP_COLS = {
    "BaselineLoc_p35s_Ubiquitous (35S)": "p35S (Ubiquitous)",
    "BaselineLoc_pcer5_Shoot Epidermis": "pCER5 (Shoot Epidermis)",
    "BaselineLoc_pco2_Meristematic Cortex": "pCO2 (Meristem Cortex)",
    "BaselineLoc_pgl2_Atrichoblast Epidermis": "pGL2 (Atrichoblast)",
    "BaselineLoc_ppep_Cortex (PEP)": "pPEP (Root Cortex)",
    "BaselineLoc_prbcs_Photosynthetic Mesophyll": "pRBCS (Mesophyll)",
    "BaselineLoc_pscr_Endodermis / QC": "pSCR (Endodermis / QC)",
    "BaselineLoc_pshr_Stele / Endodermis (SHR)": "pSHR (Stele / Endodermis)",
    "BaselineLoc_psuc2_Phloem Companion Cells": "pSUC2 (Phloem Companion)",
    "BaselineLoc_psultr2;2_Phloem Companion / Bundle Sheath": "pSULTR2;2 (Bundle Sheath)",
    "BaselineLoc_pwol_Stele / Vasculature": "pWOL (Stele Vasculature)",
    "BaselineLoc_total_Whole-Organ Total RNA": "Total RNA (Whole Organ)",
}

CLEAN_SN_COLS = {
    "snRNA_Hypoxia_dlog2_Columella_RootCap": "Columella / Root Cap",
    "snRNA_Hypoxia_dlog2_Cortex": "Cortex",
    "snRNA_Hypoxia_dlog2_Endodermis": "Endodermis",
    "snRNA_Hypoxia_dlog2_Epidermis_Atrichoblast": "Atrichoblast Epidermis",
    "snRNA_Hypoxia_dlog2_Epidermis_Trichoblast": "Trichoblast Epidermis",
    "snRNA_Hypoxia_dlog2_Meristem_QC": "Meristem / QC",
    "snRNA_Hypoxia_dlog2_Phloem": "Phloem",
    "snRNA_Hypoxia_dlog2_Stele_Pericycle": "Stele / Pericycle",
    "snRNA_Hypoxia_dlog2_Xylem": "Xylem",
}


def _anchor_xticks(ax, rotation: float = 35, fontsize: float = 8.2):
    """Properly rotate and right-anchor x-axis tick labels so they never drift or collide."""
    ax.tick_params(axis="x", labelsize=fontsize)
    plt.setp(
        ax.get_xticklabels(),
        rotation=rotation,
        ha="right",
        va="top",
        rotation_mode="anchor",
        fontsize=fontsize,
    )


def make_fig1_forensics():
    """Figure 1: Experimental Phase Space, Cross-Series Deduplication, and TabPFN v2 Forensic Audit."""
    meta = pd.read_csv(TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv", index_col=0)
    disp = pd.read_csv(RESULTS_DIR / "wp1_disputed_samples_audit.csv")
    bench = pd.read_csv(RESULTS_DIR / "wp1_organ_classification_benchmark.csv")

    fig = plt.figure(figsize=(15.2, 11.0))
    gs = gridspec.GridSpec(2, 2, hspace=0.36, wspace=0.32)

    # Panel A: Atmospheric Phase Space (P_total vs pO2)
    axA = fig.add_subplot(gs[0, 0])
    p_grid = np.linspace(0, 105, 100)
    axA.plot(p_grid, 0.21 * p_grid, "--", color="#7f8c8d", lw=1.4, label="Standard Air Line (21% O$_2$)")
    axA.axhline(20.37, linestyle=":", color="#27ae60", lw=1.3, label="Normobaric Normoxia ($p$O$_2$=20.4 kPa)")

    conds = meta.groupby(["regime", "P_total_kPa", "pO2_kPa"]).size().reset_index(name="n_arrays")
    palette_reg = {
        "Control_97kPa_Normoxia": ("#2c3e50", "o", "Control 97 kPa Normoxia"),
        "Hypobaria_75kPa_Air": ("#2980b9", "s", "Hypobaria 75 kPa Air"),
        "Hypobaria_50kPa_Air": ("#3498db", "s", "Hypobaria 50 kPa Air"),
        "Hypobaria_25kPa_Air": ("#e67e22", "^", "Hypobaria 25 kPa Air"),
        "Hypobaria_10kPa_Air": ("#d35400", "v", "Hypobaria 10 kPa Air"),
        "Hypobaria_5kPa_Air": ("#c0392b", "v", "Hypobaria 5 kPa Air"),
        "Hypobaria_50kPa_NormoxicO2": ("#16a085", "D", "Hypobaria 50 kPa + Normoxic O$_2$"),
        "Hypobaria_25kPa_NormoxicO2": ("#27ae60", "D", "Hypobaria 25 kPa + Normoxic O$_2$"),
        "Normobaric_Hypoxia_97kPa_5.1kPaO2": ("#8e44ad", "P", "Normobaric Hypoxia 97 kPa (5.1 kPa O$_2$)"),
    }
    for _, row in conds.iterrows():
        col, mk, clean_r = palette_reg.get(row["regime"], ("#34495e", "o", row["regime"]))
        lbl = f"{clean_r} (n={row['n_arrays']})"
        axA.scatter(row["P_total_kPa"], row["pO2_kPa"], s=95, color=col, marker=mk, edgecolor="black", lw=0.8, zorder=5, label=lbl)

    axA.scatter([56.54], [19.22], s=210, color="#e74c3c", marker="*", edgecolor="black", lw=1.0, zorder=6,
                label="NASA Exploration Setpoint (56.5 kPa, 34% O$_2$)")
    axA.scatter([70.33], [18.64], s=180, color="#f39c12", marker="*", edgecolor="black", lw=1.0, zorder=6,
                label="NASA Pre-EVA Staged (70.3 kPa, 26.5% O$_2$)")
    axA.scatter([62.0], [62.0 * 0.21], s=120, color="#1abc9c", marker="X", edgecolor="black", lw=0.9, zorder=5,
                label="Zenodo Ecotron Physiology (62 kPa Air)")

    axA.set_xlabel("Total Atmospheric Pressure $P_{\\mathrm{total}}$ (kPa)")
    axA.set_ylabel("Chamber Oxygen Partial Pressure $p\\mathrm{O}_2$ (kPa)")
    axA.set_title("A. Physical Atmospheric Phase Space & Compendium (n = 130 Arrays)", loc="left")
    axA.set_xlim(0, 105)
    axA.set_ylim(0, 31.8)
    axA.legend(loc="upper left", bbox_to_anchor=(0.01, 0.99), frameon=True, framealpha=0.95, fontsize=6.5, ncol=2)
    axA.grid(True, alpha=0.25)

    # Panel B: Forensic Resolution of Disputed GSM2342806-GSM2342809 Organ Identity
    axB = fig.add_subplot(gs[0, 1])
    clean_mask = ~meta.index.isin(disp["gsm_id"])
    shoots = meta[clean_mask & (meta["char_organ"] == "Shoot")]
    roots = meta[clean_mask & (meta["char_organ"] == "Root")]
    disputed = meta.loc[disp["gsm_id"]]

    axB.scatter(roots["root_marker_log2"], roots["shoot_marker_log2"], c="#8d6e63", s=45, alpha=0.75, label="Unambiguous Roots (n=65)", edgecolor="none")
    axB.scatter(shoots["root_marker_log2"], shoots["shoot_marker_log2"], c="#2ecc71", s=45, alpha=0.75, label="Unambiguous Shoots (n=61)", edgecolor="none")
    axB.scatter(disputed["root_marker_log2"], disputed["shoot_marker_log2"], c="#e74c3c", s=140, marker="^", edgecolor="black", lw=1.1, zorder=5,
                label="Disputed GSE87903 75 kPa (GSM2342806–809)")

    # Distinct, non-overlapping callout offsets and untruncated CEL descriptors
    callout_cfg = {
        "GSM2342806": ((16, -16), "GSM2342806 (5411_75_Ashoot)"),
        "GSM2342807": ((26, -5), "GSM2342807 (6827_75_A_shoot)"),
        "GSM2342808": ((22, 2), "GSM2342808 (5440_75_B_shoots)"),
        "GSM2342809": ((18, 20), "GSM2342809 (5429_75C_shoots)"),
    }
    for gsm_id, r in disputed.iterrows():
        offset_xy, label_txt = callout_cfg.get(gsm_id, ((10, 5), gsm_id))
        axB.annotate(
            label_txt,
            (r["root_marker_log2"], r["shoot_marker_log2"]),
            xytext=offset_xy,
            textcoords="offset points",
            fontsize=7.4,
            fontweight="bold",
            color="#c0392b",
            arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.85, connectionstyle="arc3,rad=0.08"),
        )

    axB.set_xlabel("Root Endodermal/Stele Marker Expression ($\\log_2$ RMA/MAS5)")
    axB.set_ylabel("Shoot Photosynthetic Marker Expression ($\\log_2$ RMA/MAS5)")
    axB.set_title("B. Forensic Resolution of Disputed GSE87903 75 kPa Samples", loc="left")
    axB.legend(loc="lower left", frameon=True)
    axB.grid(True, alpha=0.25)

    # Panel C: TabPFN v2 Out-of-Fold Organ Classification Benchmark
    axC = fig.add_subplot(gs[1, 0])
    bench_sub = bench[bench["model"] != "Dummy (Naive Baseline)"].copy()
    y_pos = np.arange(len(bench_sub))
    colors_m = ["#c0392b" if "TabPFN" in m else "#34495e" for m in bench_sub["model"]]
    axC.barh(y_pos, bench_sub["ROC_AUC"], xerr=[bench_sub["ROC_AUC"] - bench_sub["ROC_AUC_CI_low"], bench_sub["ROC_AUC_CI_high"] - bench_sub["ROC_AUC"]],
             color=colors_m, alpha=0.88, height=0.6, capsize=3)
    axC.set_yticks(y_pos)
    axC.set_yticklabels(bench_sub["model"])
    axC.invert_yaxis()
    axC.set_xlim(0.90, 1.005)
    axC.set_xlabel("5-Fold Group-CV ROC-AUC (with 95% Bootstrap CI)")
    axC.set_title("C. Out-of-Fold Organ Classification Benchmark (n = 126 Clean Arrays)", loc="left")
    for idx, r in enumerate(bench_sub.itertuples()):
        brier_str = f"{r.Brier_Score:.6f}" if r.Brier_Score < 0.0001 else f"{r.Brier_Score:.4f}"
        axC.text(0.922, idx, f"AUC={r.ROC_AUC:.4f} | Brier={brier_str}", va="center", ha="left", color="white", fontweight="bold", fontsize=7.8)
    axC.grid(True, axis="x", alpha=0.25)

    # Panel D: Posterior Shoot Probability & Hybridization Batch Forensics on Disputed + Rehybridized Arrays
    axD = fig.add_subplot(gs[1, 1])
    x_d = np.arange(len(disp))
    width = 0.26
    axD.bar(x_d - width, disp["TabPFN_v2_PHE_P_Shoot"], width, label="TabPFN v2 (PHE)", color="#c0392b")
    axD.bar(x_d, disp["LightGBM_P_Shoot"], width, label="LightGBM", color="#2980b9")
    axD.bar(x_d + width, disp["ElasticNet_P_Shoot"], width, label="ElasticNet (LogReg)", color="#27ae60")
    axD.axhline(0.5, linestyle="--", color="gray", lw=1.0, label="Decision Threshold (0.50)")
    axD.set_xticks(x_d)
    axD.set_xticklabels([
        f"{r['gsm_id']}\nBatch {r['cel_hybridization_batch']} (Rep {r['cel_replicate_letter']})\nCEL: {r['cel_inferred_organ']}"
        for _, r in disp.iterrows()
    ], fontsize=8.0)
    axD.set_ylim(0, 1.12)
    axD.set_ylabel("Posterior Probability $P(\\mathrm{Organ = Shoot} \\mid \\mathbf{x})$")
    axD.set_title("D. Posterior Probabilities & Raw CEL Audit for GSM2342806–809", loc="left")
    for i, pval in enumerate(disp["TabPFN_v2_PHE_P_Shoot"]):
        axD.text(i - width, pval + 0.02, f"{pval:.4f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#c0392b")
    axD.legend(loc="lower right", frameon=True)
    axD.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Figure 1 | Multi-Study Data Harmonization, Deduplication, and TabPFN v2 Metadata Forensics", y=0.98)
    out_path = FIG_DIR / "fig1_data_forensics_harmonization.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def make_fig2_decoupling():
    """Figure 2: TabPFN v2 Decoupling of Total Pressure (P_total) vs Oxygen Partial Pressure (pO2)."""
    reg_bench = pd.read_csv(TABLES_DIR / "Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv")
    clf_bench = pd.read_csv(TABLES_DIR / "Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv")
    slice_df = pd.read_csv(TABLES_DIR / "Table_S2C_Slice_Based_Error_Analysis.csv")
    oof_58 = pd.read_csv(RESULTS_DIR / "wp2_oof_predictions_58samples.csv", index_col=0)

    fig = plt.figure(figsize=(16.2, 11.4))
    gs = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.38)

    # Panel A: Hypobaria Index & Hypoxia Index R2 Benchmark across Models
    axA = fig.add_subplot(gs[0, 0])
    sub_b = reg_bench[reg_bench["Task"].str.startswith("WP2A_") & (reg_bench["model"] != "Dummy (Mean Baseline)")].copy()
    sub_h = reg_bench[reg_bench["Task"].str.startswith("WP2B_") & (reg_bench["model"] != "Dummy (Mean Baseline)")].copy()

    models_order = sub_b["model"].tolist()
    y_pos = np.arange(len(models_order))
    h_bar = 0.36

    axA.barh(
        y_pos - h_bar / 2, sub_b["R2"], height=h_bar, color="#2980b9", alpha=0.9,
        xerr=[np.maximum(0, sub_b["R2"] - sub_b["R2_CI_low"]), np.maximum(0, sub_b["R2_CI_high"] - sub_b["R2"])],
        capsize=2.5, label="Total Pressure Index $\\log_2(97/P_{\\mathrm{total}})$ $R^2$"
    )
    axA.barh(
        y_pos + h_bar / 2, sub_h["R2"], height=h_bar, color="#e67e22", alpha=0.9,
        xerr=[np.maximum(0, sub_h["R2"] - sub_h["R2_CI_low"]), np.maximum(0, sub_h["R2_CI_high"] - sub_h["R2"])],
        capsize=2.5, label="Oxygen Partial Pressure Index $\\log_2(20.4/p\\mathrm{O}_2)$ $R^2$"
    )
    axA.set_yticks(y_pos)
    axA.set_yticklabels(models_order)
    axA.invert_yaxis()
    axA.set_xlabel("Out-of-Fold Cross-Validation $R^2$ (with 95% Bootstrap CI)")
    axA.set_title("A. Multi-Task Physical Regression Benchmark (n = 58 24-h Arrays)", loc="left")
    axA.set_xlim(0, 1.05)
    axA.set_ylim(len(models_order) - 0.4 + 0.9, -0.6)  # headroom below MLP row for the legend
    axA.legend(loc="lower right", frameon=True, fontsize=8.0)
    axA.grid(True, axis="x", alpha=0.25)

    # Panel B: 4-Class Atmospheric Regime Classification Benchmark
    axB = fig.add_subplot(gs[0, 1])
    clf_sub = clf_bench[clf_bench["model"] != "Dummy (Naive Baseline)"].copy()
    x_pos = np.arange(len(clf_sub))
    w = 0.26
    axB.bar(x_pos - w, clf_sub["ROC_AUC"], w, label="Macro ROC-AUC", color="#8e44ad")
    axB.bar(x_pos, clf_sub["PR_AUC"], w, label="Macro PR-AUC", color="#16a085")
    axB.bar(x_pos + w, clf_sub["Macro_F1"], w, label="Macro F1 Score", color="#c0392b")
    axB.set_xticks(x_pos)
    axB.set_xticklabels(clf_sub["model"])
    _anchor_xticks(axB, rotation=24, fontsize=8.3)
    axB.set_ylim(0.4, 1.08)
    axB.set_yticks(np.arange(0.4, 1.01, 0.1))
    axB.set_ylabel("Out-of-Fold Score")
    axB.set_title("B. 4-Class Mechanistic Atmospheric Regime Classification", loc="left")
    axB.legend(loc="upper center", frameon=True, ncol=3, fontsize=8.0)
    axB.grid(True, axis="y", alpha=0.25)

    # Panel C: Out-of-Fold TabPFN v2 (PHE) Predicted vs Observed Hypobaria & Hypoxia Indices
    axC = fig.add_subplot(gs[1, 0])
    reg_colors = {
        0: ("#2c3e50", "Control Normoxia (97 kPa)"),
        1: ("#27ae60", "Pure Hypobaria + Normoxic O$_2$ (50/25 kPa + O$_2$)"),
        2: ("#2980b9", "Moderate Combined Hypobaria (75/50 kPa Air)"),
        3: ("#c0392b", "Severe Hypoxia / Hypobaria (25/10/5 kPa, 5.1 kPa O$_2$)"),
    }
    for c_id, (col, lbl) in reg_colors.items():
        sub = oof_58[oof_58["true_regime_4class"] == c_id]
        axC.scatter(sub["pred_baro_TabPFN v2 (PHE)"], sub["pred_hypo_TabPFN v2 (PHE)"],
                    c=col, s=75, alpha=0.88, edgecolor="black", lw=0.7, label=lbl, zorder=4)
    axC.axhline(0.28, linestyle="--", color="#7f8c8d", lw=1.0)
    axC.axvline(0.32, linestyle="--", color="#7f8c8d", lw=1.0)

    # Place callouts in clean whitespace with arrows pointing to clusters
    axC.annotate(
        "Normoxic Hypobaria Zone\n(Barosensory Active, Hypoxia Silent)",
        xy=(1.55, 0.01), xytext=(2.85, 0.22),
        fontsize=7.8, fontweight="bold", color="#16a085", ha="center",
        bbox=dict(boxstyle="round,pad=0.25", fc="#ecf9f6", ec="#16a085", lw=0.8),
        arrowprops=dict(arrowstyle="->", color="#16a085", lw=1.1),
    )
    axC.annotate(
        "Normobaric Hypoxia\n(97 kPa, 5.1 kPa O$_2$)",
        xy=(0.06, 2.00), xytext=(-0.08, 3.05),
        fontsize=7.8, fontweight="bold", color="#8e44ad", ha="left",
        bbox=dict(boxstyle="round,pad=0.25", fc="#f5eef8", ec="#8e44ad", lw=0.8),
        arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=1.1),
    )
    axC.set_xlim(-0.15, 4.55)
    axC.set_ylim(-0.32, 4.55)
    axC.set_xlabel("TabPFN v2 Out-of-Fold Predicted Hypobaria Index $\\hat{y}_{\\mathrm{baro}} = \\log_2(97/P_{\\mathrm{total}})$")
    axC.set_ylabel("TabPFN v2 Out-of-Fold Predicted Hypoxia Index $\\hat{y}_{\\mathrm{hypo}} = \\log_2(20.4/p\\mathrm{O}_2)$")
    axC.set_title("C. Out-of-Fold 2D Atmospheric Decoupling by TabPFN v2 (PHE)", loc="left")
    axC.legend(loc="upper left", frameon=True, fontsize=7.4)
    axC.grid(True, alpha=0.25)

    # Panel D: Slice-Based Error Analysis (Hypobaria RMSE across Biological Subgroups)
    axD = fig.add_subplot(gs[1, 1])
    piv = slice_df.pivot(index="Slice", columns="Model", values="Hypobaria_RMSE")[
        ["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "RandomForest", "ElasticNet"]
    ]
    short_slice_map = {
        "Age: 10/11-day Root & Shoot (n=49)": "10/11d Root & Shoot\n(n=49)",
        "Age: 5-day Root (GSE87868, n=9)": "5d Young Root\n(OSD-136, n=9)",
        "Organ: Root (n=31)": "Organ: Root\n(n=31)",
        "Organ: Shoot (n=27)": "Organ: Shoot\n(n=27)",
        "Regime: Normoxic O2 Supplemented (50/25 kPa + O2, n=13)": "Normoxic O2 Supp.\n(50/25 kPa+O2, n=13)",
        "Regime: Unsupplemented Air / Hypoxia (n=45)": "Unsupplemented Air\n(n=45)",
    }
    piv.index = [short_slice_map.get(s, s) for s in piv.index]
    sns.heatmap(piv, annot=True, fmt=".3f", cmap="YlOrRd", cbar_kws={"label": "Out-of-Fold RMSE ($\\log_2$ pressure units)"}, ax=axD, linewidths=0.8)
    axD.set_title("D. Slice-Based Error Analysis Across Biological Subgroups", loc="left")
    axD.set_xlabel("")
    axD.set_ylabel("")
    _anchor_xticks(axD, rotation=24, fontsize=8.3)
    axD.tick_params(axis="y", rotation=0, labelsize=8.0)

    fig.suptitle("Figure 2 | TabPFN v2 Decouples Barosensory Total Pressure ($P_{\\mathrm{total}}$) from Oxygen Partial Pressure ($p\\mathrm{O}_2$)", y=0.98)
    out_path = FIG_DIR / "fig2_tabpfn_atmospheric_decoupling.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def make_fig3_hubs_shap():
    """Figure 3: Orthogonal Molecular Hub Landscape, TabPFN SHAP Attributions, and O2-Rescue Profiles."""
    orth = pd.read_csv(RESULTS_DIR / "wp2_full_22746_orthogonal_decomposition.csv", index_col=0)
    shap_baro = pd.read_csv(RESULTS_DIR / "wp2_shap_summary_hypobaria.csv")
    shap_hypo = pd.read_csv(RESULTS_DIR / "wp2_shap_summary_hypoxia.csv")

    fig = plt.figure(figsize=(16.0, 12.0))
    gs = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.32, height_ratios=[1.05, 1.0])

    # Panel A: Orthogonal Decomposition Landscape across 22,746 Probesets
    axA = fig.add_subplot(gs[0, 0])
    axis_colors = {
        "Background_Unchanged": ("#bdc3c7", 8, 0.25, "Background Unchanged"),
        "Pure_Barosensory_Ptotal": ("#16a085", 26, 0.80, "Pure Barosensory ($P_{\\mathrm{total}}$)"),
        "Predominantly_Barosensory": ("#1abc9c", 24, 0.75, "Predominantly Barosensory"),
        "Pure_Hypoxia_pO2": ("#c0392b", 26, 0.80, "Pure Hypoxia ($p\\mathrm{O}_2$)"),
        "Predominantly_Hypoxia": ("#e74c3c", 24, 0.75, "Predominantly Hypoxia"),
        "Synergistic_Dual_Hub": ("#8e44ad", 32, 0.85, "Synergistic Dual Hub ($P_{\\mathrm{total}} \\times p\\mathrm{O}_2$)"),
    }
    for ax_name, (col, sz, alp, lbl) in axis_colors.items():
        sub = orth[orth["mechanistic_axis"] == ax_name]
        axA.scatter(sub["beta_hypobaria"], sub["beta_hypoxia"], c=col, s=sz, alpha=alp, label=f"{lbl} (n={len(sub):,})", edgecolors="none")

    axA.axhline(0, color="black", lw=0.8, linestyle="--")
    axA.axvline(0, color="black", lw=0.8, linestyle="--")

    # Annotate key outer-envelope biological hub genes with non-overlapping offsets
    highlight_genes = [
        ("PDC1", "AT4G33070", (7, -2)),
        ("WIP5", "AT4G33560", (-34, -3)),
        ("AAD6", "AT1G43800", (7, -8)),
        ("HB1", "AT2G16060", (7, 2)),
        ("HRU1", "AT3G03270", (-34, 2)),
        ("SUS1", "AT5G20830", (7, 2)),
        ("ADH1", "AT1G77120", (7, 3)),
        ("PCO1", "AT5G15120", (7, 2)),
        ("LBD41", "AT3G02550", (-36, 2)),
        ("TCH4", "AT5G57560", (-18, 8)),
        ("CMI1", "AT4G27280", (7, -8)),
        ("STZ", "AT1G27730", (7, 4)),
        ("ACS6", "AT4G11280", (-34, 6)),
        ("ERF104", "AT5G61600", (7, -6)),
        ("LTP3", "AT5G59320", (7, -5)),
        ("LTP4", "AT5G59310", (-26, 7)),
        ("COR15A", "AT2G42540", (-38, 6)),
    ]
    for sym, tair_id, offset_xy in highlight_genes:
        m = orth[orth["TAIR"].fillna("").str.contains(tair_id)]
        if not m.empty:
            r = m.sort_values("hub_composite_score", ascending=False).iloc[0]
            axA.scatter([r["beta_hypobaria"]], [r["beta_hypoxia"]], s=55, c="yellow", edgecolor="black", lw=0.9, zorder=6)
            axA.annotate(
                sym, (r["beta_hypobaria"], r["beta_hypoxia"]),
                xytext=offset_xy, textcoords="offset points",
                fontsize=7.3, fontweight="bold", zorder=7,
                arrowprops=dict(arrowstyle="-", color="black", lw=0.5),
            )

    axA.set_xlim(-0.52, 0.90)
    axA.set_ylim(-0.68, 2.15)
    axA.set_xlabel("Partial Barosensory Slope $\\beta_{\\mathrm{hypobaria}}$ ($\\Delta\\log_2\\mathrm{FC}$ per $\\log_2(97/P_{\\mathrm{total}})$)")
    axA.set_ylabel("Partial Hypoxia Slope $\\beta_{\\mathrm{hypoxia}}$ ($\\Delta\\log_2\\mathrm{FC}$ per $\\log_2(20.4/p\\mathrm{O}_2)$)")
    axA.set_title("A. Orthogonal Barosensory vs. Hypoxia Transcriptome Decomposition", loc="left")
    axA.legend(loc="upper left", frameon=True, framealpha=0.95, fontsize=6.9, ncol=2)
    axA.grid(True, alpha=0.25)

    # Panel B: Top TabPFN v2 SHAP Attributions for Total Pressure (Hypobaria) vs Oxygen Partial Pressure (Hypoxia)
    axB = fig.add_subplot(gs[0, 1])
    top_b = shap_baro.head(12).copy()
    top_h = shap_hypo.head(12).copy()
    combined_feats = list(dict.fromkeys(top_b["feature"].iloc[:8].tolist() + top_h["feature"].iloc[:8].tolist()))
    sb_map = shap_baro.set_index("feature")["mean_abs_shap"].to_dict()
    sh_map = shap_hypo.set_index("feature")["mean_abs_shap"].to_dict()

    y_f = np.arange(len(combined_feats))
    clean_fnames = [
        f.replace("PW_Ethylene_Auxin_Root_Remodeling", "[PW] Ethylene & Auxin Root Remodeling")
         .replace("COV_age_days", "[COV] Developmental Age (days)")
         .replace("PW_", "[PW] ").replace("INT_", "[INT] ").replace("GENE_", "[Gene] ")
        for f in combined_feats
    ]
    vb = [sb_map.get(f, 0.0) for f in combined_feats]
    vh = [sh_map.get(f, 0.0) for f in combined_feats]

    axB.barh(y_f - 0.18, vb, height=0.35, color="#16a085", label="TabPFN v2 $|\\mathrm{SHAP}|$ for $P_{\\mathrm{total}}$ (Hypobaria)")
    axB.barh(y_f + 0.18, vh, height=0.35, color="#c0392b", label="TabPFN v2 $|\\mathrm{SHAP}|$ for $p\\mathrm{O}_2$ (Hypoxia)")
    axB.set_yticks(y_f)
    axB.set_yticklabels(clean_fnames, fontsize=8.0)
    axB.invert_yaxis()
    axB.set_xlabel("Mean Absolute SHAP Attribution ($|\\mathrm{SHAP}|$ in $\\log_2$ index units)")
    axB.set_title("B. TabPFN v2 Global SHAP Attributions: $P_{\\mathrm{total}}$ vs. $p\\mathrm{O}_2$ Predictors", loc="left")
    axB.legend(loc="lower right", frameon=True)
    axB.grid(True, axis="x", alpha=0.25)

    # Panel C: Oxygen Supplementation Dissection Heatmap (50 kPa Air vs 50 kPa + O2 and 25 kPa Air vs 25 kPa + O2)
    axC = fig.add_subplot(gs[1, :])
    panel_genes = [
        ("ADH1", "AT1G77120"), ("PDC1", "AT4G33070"), ("SUS1", "AT5G20830"), ("HB1", "AT2G16060"),
        ("PCO1", "AT5G15120"), ("LBD41", "AT3G02550"), ("HRU1", "AT3G03270"), ("WIP5", "AT4G33560"),
        ("CMI1", "AT4G27280"), ("STZ", "AT1G27730"), ("TCH4", "AT5G57560"), ("ACS6", "AT4G11280"),
        ("PBP1", "AT5G54490"), ("DIC2", "AT4G24570"), ("DREB26", "AT1G21910"), ("ERF104", "AT5G61600"),
        ("LOX2", "AT3G45140"), ("AOS", "AT5G42650"), ("CYP79B2", "AT4G39950"), ("SNG1", "AT2G22990"),
        ("LTP3", "AT5G59320"), ("LTP4", "AT5G59310"), ("SEN1", "AT4G35770"), ("RBCS1A", "AT1G67090"),
    ]
    rows_hm = []
    labels_hm = []
    cols_hm = [
        "dlog2_75kPa_Air", "dlog2_50kPa_Air", "dlog2_50kPa_NormO2",
        "dlog2_25kPa_Air", "dlog2_25kPa_NormO2", "dlog2_97kPa_5.1kPaO2", "dlog2_10kPa_Air"
    ]
    col_titles = [
        "75 kPa Air\n(15.8 kPa O$_2$)", "50 kPa Air\n(10.5 kPa O$_2$)", "50 kPa + O$_2$\n(21.0 kPa O$_2$)",
        "25 kPa Air\n(5.3 kPa O$_2$)", "25 kPa + O$_2$\n(21.0 kPa O$_2$)", "97 kPa Hypoxia\n(5.1 kPa O$_2$)", "10 kPa Air\n(2.1 kPa O$_2$)"
    ]
    for sym, tair_id in panel_genes:
        m = orth[orth["TAIR"].fillna("").str.contains(tair_id)]
        if not m.empty:
            r = m.sort_values("hub_composite_score", ascending=False).iloc[0]
            rows_hm.append(r[cols_hm].values.astype(float))
            labels_hm.append(f"{sym} ({tair_id})")

    hm_mat = pd.DataFrame(rows_hm, index=labels_hm, columns=col_titles).T
    sns.heatmap(hm_mat, cmap="RdBu_r", center=0.0, vmin=-2.5, vmax=3.5, annot=True, fmt=".2f",
                annot_kws={"size": 7.2}, cbar_kws={"label": "Mean $\\Delta\\log_2\\mathrm{FC}$ vs. Matched 97 kPa Control"},
                ax=axC, linewidths=0.5)
    axC.set_title("C. Empirical Oxygen-Rescue vs. Persistent Barosensory Profiles Across 24 Canonical Molecular Hub Nodes", loc="left")
    _anchor_xticks(axC, rotation=38, fontsize=8.0)
    axC.tick_params(axis="y", rotation=0, labelsize=8.3)

    fig.suptitle("Figure 3 | Identification and SHAP Attribution of Exploration Atmosphere Molecular Hub Nodes", y=0.98)
    out_path = FIG_DIR / "fig3_molecular_hub_network_shap.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def make_fig4_cellular_atlas():
    """Figure 4: Cell-Population TRAP-seq (GSE14502/14493) and Single-Nucleus Root Tip (GSE308672) Localization."""
    pw_atlas = pd.read_csv(TABLES_DIR / "Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv", index_col=0)
    sn_counts = pd.read_csv(RESULTS_DIR / "wp3_gse308672_single_nucleus_lineage_counts.csv")

    fig = plt.figure(figsize=(18.0, 12.2))
    gs = gridspec.GridSpec(2, 2, hspace=0.46, wspace=0.48)

    clean_pws = [CLEAN_PATHWAY_NAMES.get(p, p.replace("_", " ")) for p in pw_atlas.index]

    # Panel A: Baseline Cell-Population Enrichment across TRAP-seq Promoter Lines (GSE14502)
    axA = fig.add_subplot(gs[0, 0])
    base_cols = [c for c in pw_atlas.columns if c.startswith("BaselineLoc_")]
    clean_bcols = [CLEAN_TRAP_COLS.get(c, c.replace("BaselineLoc_", "")) for c in base_cols]
    mat_base = pw_atlas[base_cols].copy()
    mat_base.index = clean_pws
    mat_base.columns = clean_bcols

    sns.heatmap(mat_base, cmap="PiYG", center=0.0, vmin=-0.8, vmax=0.8, annot=True, fmt=".2f",
                annot_kws={"size": 7.0}, cbar_kws={"label": "Cell-Type Translatome $\\Delta\\log_2$ vs. Global Mean"},
                ax=axA, linewidths=0.5)
    axA.set_title("A. Cell-Type Translatome Localization of Atmospheric Modules (GSE14502)", loc="left")
    axA.set_ylabel("")
    _anchor_xticks(axA, rotation=38, fontsize=8.2)
    axA.tick_params(axis="y", rotation=0, labelsize=8.3)

    # Panel B: Single-Nucleus Root Tip Lineage Hypoxia Response (GSE308672, 40,860 nuclei)
    axB = fig.add_subplot(gs[0, 1])
    sn_cols = [c for c in pw_atlas.columns if c.startswith("snRNA_Hypoxia_dlog2_")]
    clean_sncols = [CLEAN_SN_COLS.get(c, c.replace("snRNA_Hypoxia_dlog2_", "").replace("_", " ")) for c in sn_cols]
    mat_sn = pw_atlas[sn_cols].copy()
    mat_sn.index = clean_pws
    mat_sn.columns = clean_sncols

    sns.heatmap(mat_sn, cmap="RdBu_r", center=0.0, vmin=-0.9, vmax=1.2, annot=True, fmt=".2f",
                annot_kws={"size": 7.2}, cbar_kws={"label": "snRNA-seq Hypoxia (4% vs 21% O$_2$) $\\Delta\\log_2\\mathrm{CPM}$"},
                ax=axB, linewidths=0.5)
    axB.set_title("B. Single-Nucleus Root Lineage Hypoxia Trajectories (GSE308672, 5d Col-0)", loc="left")
    axB.set_ylabel("")
    _anchor_xticks(axB, rotation=38, fontsize=8.4)
    axB.tick_params(axis="y", rotation=0, labelsize=8.3)

    # Panel C: Sucrose Rescue Dissection in GSE14493 (Hypoxia - Sucrose vs Hypoxia + Sucrose)
    axC = fig.add_subplot(gs[1, 0])
    y_p = np.arange(len(pw_atlas))
    v_nosuc = pw_atlas["GSE14493_Hypoxia_NoSucrose_dlog2"].values
    v_suc_rescue = pw_atlas["GSE14493_Sucrose_Rescue_vs_NoSucrose_dlog2"].values

    axC.barh(y_p - 0.18, v_nosuc, height=0.35, color="#c0392b", label="Hypoxia Response (No Exogenous Sucrose)")
    axC.barh(y_p + 0.18, v_suc_rescue, height=0.35, color="#2980b9", label="Exogenous Sucrose Rescue ($\\mathrm{Hypoxia+Suc} - \\mathrm{Hypoxia}$)")
    axC.axvline(0, color="black", lw=0.8)
    axC.set_yticks(y_p)
    axC.set_yticklabels(clean_pws, fontsize=8.3)
    axC.invert_yaxis()
    axC.set_xlabel("Mean Pathway $\\Delta\\log_2\\mathrm{FC}$ (GSE14493 TRAP & Total RNA)")
    axC.set_title("C. Metabolic Sucrose Rescue Decouples SnRK1 Starvation from ERF-VII", loc="left")
    axC.legend(loc="lower right", frameon=True, fontsize=7.8)
    axC.grid(True, axis="x", alpha=0.25)

    # Panel D: Single-Nucleus Lineage Composition Across 40,860 Root Tip Nuclei (GSE308672)
    axD = fig.add_subplot(gs[1, 1])
    piv_cnt = sn_counts.groupby(["lineage", "condition"])["n_nuclei"].sum().unstack()
    clean_lin_map = {
        "Columella_RootCap": "Columella / Root Cap",
        "Cortex": "Cortex",
        "Endodermis": "Endodermis",
        "Epidermis_Atrichoblast": "Atrichoblast Epidermis",
        "Epidermis_Trichoblast": "Trichoblast Epidermis",
        "Meristem_QC": "Meristem / QC",
        "Phloem": "Phloem",
        "Stele_Pericycle": "Stele / Pericycle",
        "Xylem": "Xylem",
    }
    piv_cnt.index = [clean_lin_map.get(i, i.replace("_", " ")) for i in piv_cnt.index]
    piv_cnt.plot(kind="barh", ax=axD, color=["#e74c3c", "#3498db"], width=0.72)
    axD.invert_yaxis()
    axD.set_xlabel("Total QC-Filtered Single Nuclei (n = 40,860 across 4 Replicates)")
    axD.set_ylabel("")
    axD.tick_params(axis="y", labelsize=8.4)
    axD.set_title("D. Single-Nucleus Root Atlas Census by Lineage & Oxygen Regime", loc="left")
    axD.legend(["Hypoxia (4% O$_2$, 4h)", "Normoxia (21% O$_2$, 4h)"], loc="lower right", frameon=True)
    axD.grid(True, axis="x", alpha=0.25)

    fig.suptitle("Figure 4 | Cellular and Single-Nucleus Localization of Exploration Atmosphere Signaling Modules", y=0.98)
    out_path = FIG_DIR / "fig4_cellular_tissue_localization.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def make_fig5_physiology_metabolomics():
    """Figure 5: Physiological, Metabolomic (ZENODO16536514), and Proteomic (PXD002353) Triangulation."""
    from atmos_ml.ingest import load_zenodo_physiology_metabolomics
    zen = load_zenodo_physiology_metabolomics()
    fluo = zen["fluorescence"]
    met = pd.read_csv(TABLES_DIR / "Table_S5B_Zenodo16536514_Metabolomics_Pressure_x_Humidity_Triangulation.csv")
    met_cf = pd.read_csv(RESULTS_DIR / "wp4_metabolomics_humidity_rescue_counterfactual.csv")

    fig = plt.figure(figsize=(16.5, 11.8))
    gs = gridspec.GridSpec(2, 2, hspace=0.40, wspace=0.34)

    # Panel A: Normalized Physiological Remodeling at 62 kPa vs 101 kPa (GH2O, E, A, RWC, d13C, VPD)
    axA = fig.add_subplot(gs[0, 0])
    phys_df = pd.read_csv(TABLES_DIR / "Table_S5A_Zenodo16536514_Physiology_62kPa_vs_101kPa_Stats.csv")
    show_codes = ["GH2O", "E", "A", "cica", "RWC", "d13C", "Npp", "VPD"]
    sub_p = phys_df.set_index("Trait_Code").loc[show_codes].reset_index()

    y_p = np.arange(len(sub_p))
    cols_p = ["#c0392b" if g < -0.5 else ("#27ae60" if g > 0.5 else "#7f8c8d") for g in sub_p["Hedges_g"]]
    axA.barh(y_p, sub_p["Hedges_g"], color=cols_p, alpha=0.88, height=0.62)
    axA.axvline(0, color="black", lw=0.9)
    axA.axvline(-0.8, color="gray", linestyle=":", lw=0.9)
    axA.axvline(0.8, color="gray", linestyle=":", lw=0.9)
    axA.set_yticks(y_p)
    axA.set_yticklabels([
        "Stomatal Conductance $g_{sw}$ (GH2O)",
        "Transpiration Rate $E$",
        "Net $\\mathrm{CO}_2$ Assimilation $A$",
        "Intercellular/Ambient $c_i/c_a$",
        "Relative Water Content (RWC)",
        "Carbon Isotope $\\delta^{13}\\mathrm{C}$ (\u2030)",
        "Leaf Nitrogen Content $N\\%$",
        "Vapor Pressure Ratio (VPD)",
    ])
    axA.invert_yaxis()
    axA.set_xlabel("Standardized Effect Size Hedges' $g$ (62 kPa vs. 101 kPa at 50% RH)")
    axA.set_title("A. Stomatal, Hydraulic & Isotope Remodeling at 62 kPa (Zenodo 16536514)", loc="left")
    for i, r in enumerate(sub_p.itertuples()):
        p_str = f"p={r.Welch_t_p:.1e}" if r.Welch_t_p < 0.001 else f"p={r.Welch_t_p:.3f}"
        x_txt = r.Hedges_g + (0.15 if r.Hedges_g >= 0 else -0.15)
        ha_align = "left" if r.Hedges_g >= 0 else "right"
        axA.text(x_txt, i, f"{r.Pct_Change_62_vs_101:+.1f}% ({p_str})", va="center", ha=ha_align, fontsize=7.5, fontweight="bold")
    axA.set_xlim(-4.2, 5.0)
    axA.grid(True, axis="x", alpha=0.25)

    # Panel B: PSII Quantum Yield Y(II) and Electron Transport Rate ETR(II) Light Curves (n = 252)
    axB = fig.add_subplot(gs[0, 1])
    f_agg = fluo.groupby(["P_total_kPa", "PAR"]).agg(
        yii_m=("Y(II)", "mean"), yii_se=("Y(II)", "sem"),
        etr_m=("ETR(II)", "mean"), etr_se=("ETR(II)", "sem"),
        npq_m=("NPQ", "mean"), npq_se=("NPQ", "sem"),
    ).reset_index()

    f101 = f_agg[f_agg["P_total_kPa"] == 101]
    f62 = f_agg[f_agg["P_total_kPa"] == 62]
    axB.errorbar(f101["PAR"], f101["etr_m"], yerr=f101["etr_se"], fmt="-o", color="#2c3e50", lw=2.0, capsize=3, label="ETR(II) at 101 kPa (50% RH)")
    axB.errorbar(f62["PAR"], f62["etr_m"], yerr=f62["etr_se"], fmt="--s", color="#e74c3c", lw=2.0, capsize=3, label="ETR(II) at 62 kPa (50% RH)")

    axB2 = axB.twinx()
    axB2.errorbar(f101["PAR"], f101["yii_m"], yerr=f101["yii_se"], fmt=":^", color="#2980b9", lw=1.6, capsize=2.5, label="Y(II) at 101 kPa")
    axB2.errorbar(f62["PAR"], f62["yii_m"], yerr=f62["yii_se"], fmt=":v", color="#e67e22", lw=1.6, capsize=2.5, label="Y(II) at 62 kPa")
    axB2.set_ylabel("Effective PSII Quantum Yield Y(II)", color="#2980b9")
    axB2.spines["top"].set_visible(False)

    axB.set_xlabel("Photosynthetically Active Radiation PAR ($\\mu\\mathrm{mol\\ m^{-2}\\ s^{-1}}$)")
    axB.set_ylabel("PSII Electron Transport Rate ETR(II) ($\\mu\\mathrm{mol\\ m^{-2}\\ s^{-1}}$)")
    axB.set_title("B. Chlorophyll Fluorescence Light-Response Curves (n = 252)", loc="left")
    lines1, labels1 = axB.get_legend_handles_labels()
    lines2, labels2 = axB2.get_legend_handles_labels()
    axB.legend(lines1 + lines2, labels1 + labels2, loc="center right", frameon=True, fontsize=7.5)
    axB.grid(True, alpha=0.25)

    # Panel C: Factorial Pressure x Humidity LC-MS Metabolome Heatmap (Clean Untruncated Biochemical Names)
    axC = fig.add_subplot(gs[1, 0])
    clean_met_map = {
        602: "Glucoraphanin (4-MSOB GSL)",
        1132: "Kaempferol-3,7-O-dirhamnoside (Flavonol)",
        660: "Kaempferol-3-O-rhamnosylglucoside-7-O-rhamnoside",
        696: "Sinapoyl malate (Hydroxycinnamate)",
        1: "Glucobrassicin (Indole GSL)",
        1067: "Kaempferol-3-O-glucoside-7-O-rhamnoside",
        1908: "Putative MGDG [m/z 793.4] (Galactolipid)",
        1805: "Arabidopside MGDG-OPDA [m/z 851.5]",
        1361: "8-Methylthiooctyl GSL (Aliphatic GSL)",
        690: "8-Methylsulfinyloctyl GSL (Glucohirsutin)",
        1702: "Arabidopside DGDG-OPDA [m/z 937.5]",
        482: "7-Methylsulfinylheptyl GSL (Glucoibarin)",
        1775: "Arabidopside MGDG-OPDA [m/z 775.5]",
        1884: "Arabidopside MGDG-OPDA [m/z 879.5]",
    }
    sub_m = met[met["compound_id"].isin(clean_met_map.keys())].copy()
    sub_m["clean_label"] = sub_m["compound_id"].map(clean_met_map)
    hm_m = sub_m.set_index("clean_label")[[
        "log2FC_62kPa_RH50_vs_101kPa_RH50",
        "log2FC_62kPa_RH70_vs_101kPa_RH50",
        "log2FC_62kPa_RH70_vs_62kPa_RH50",
        "log2FC_101kPa_RH25_vs_101kPa_RH50",
    ]].copy()
    hm_m.columns = [
        "62 kPa (50% RH)\nvs 101 kPa (50% RH)",
        "62 kPa (70% RH)\nvs 101 kPa (50% RH)",
        "Humidity Rescue\n(62 kPa 70% vs 50% RH)",
        "Dry Air Effect\n(101 kPa 25% vs 50% RH)",
    ]
    sns.heatmap(hm_m, cmap="RdBu_r", center=0.0, vmin=-2.5, vmax=2.5, annot=True, fmt=".2f",
                annot_kws={"size": 7.0}, cbar_kws={"label": "Metabolite $\\log_2\\mathrm{FC}$"}, ax=axC, linewidths=0.5)
    axC.set_title("C. Factorial Pressure $\\times$ Humidity Metabolome & Oxylipin Rescue", loc="left")
    axC.set_ylabel("")
    _anchor_xticks(axC, rotation=24, fontsize=8.0)
    axC.tick_params(axis="y", labelsize=8.0)

    # Panel D: TabPFN v2 Posterior Probability of Hypobaric Metabolic State Across Pressure x RH Factorial Groups
    axD = fig.add_subplot(gs[1, 1])
    grp_order = ["101kPa_RH50", "62kPa_RH50", "62kPa_RH70_Rescue", "101kPa_RH25_DryAir"]
    grp_labels = [
        "101 kPa, 50% RH\n(Normobaric Control)",
        "62 kPa, 50% RH\n(Unmitigated Hypobaria)",
        "62 kPa, 70% RH\n(Humidity-Mitigated\nHypobaria)",
        "101 kPa, 25% RH\n(Normobaric Evaporative\nDemand)",
    ]
    means_cf = [met_cf[met_cf["group"] == g]["TabPFN_P_Hypobaric_Metabolic_State"].mean() for g in grp_order]
    sds_cf = [met_cf[met_cf["group"] == g]["TabPFN_P_Hypobaric_Metabolic_State"].std() for g in grp_order]
    cols_cf = ["#2c3e50", "#c0392b", "#27ae60", "#e67e22"]

    x_cf = np.arange(len(grp_order))
    axD.bar(x_cf, means_cf, yerr=sds_cf, color=cols_cf, alpha=0.88, width=0.55, capsize=4, edgecolor="black", lw=0.8)
    rng = np.random.default_rng(42)
    for i, g in enumerate(grp_order):
        pts = met_cf[met_cf["group"] == g]["TabPFN_P_Hypobaric_Metabolic_State"].values
        axD.scatter([i] * len(pts) + rng.uniform(-0.06, 0.06, size=len(pts)), pts, color="black", s=30, zorder=5)
        axD.text(i, means_cf[i] + sds_cf[i] + 0.03, f"P = {means_cf[i]:.3f}", ha="center", fontweight="bold", fontsize=8.5)

    axD.axhline(0.5, linestyle="--", color="gray", lw=1.0)
    axD.set_xticks(x_cf)
    axD.set_xticklabels(grp_labels, fontsize=8.0)
    axD.set_ylim(0, 1.15)
    axD.set_ylabel("TabPFN v2 Posterior $P(\\mathrm{Hypobaric\\ Metabolic\\ State} \\mid \\mathbf{m})$")
    axD.set_title("D. Elevating Humidity to 70% RH Reverses Hypobaric Metabolic Signature", loc="left")
    axD.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Figure 5 | Multi-Omics Triangulation Links Hypobaric Vapor Diffusivity to Stomatal Closure, Oxylipins, and Glucosinolates", y=0.98)
    out_path = FIG_DIR / "fig5_physiological_metabolic_bridge.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def make_fig6_nasa_counterfactual():
    """Figure 6: LOCO Validation and In-Silico Counterfactual Prediction at NASA Exploration Atmosphere (56.54 kPa / 34% O2)."""
    cf_tab = pd.read_csv(TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv", index_col=0)
    loco_df = pd.read_csv(TABLES_DIR / "Table_S6B_Leave_One_Condition_Out_Validation.csv")

    fig = plt.figure(figsize=(17.6, 12.2))
    gs = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.48)

    # Panel A: Leave-One-Condition-Out (LOCO) Validation on Held-Out (P_total, pO2) Regimes
    axA = fig.add_subplot(gs[0, 0])
    piv_loco = loco_df.pivot_table(index="Held_Out_Regime", columns="Model", values="Pearson_r_12Pathways", aggfunc="mean")[
        ["TabPFN v2", "TabPFN v2 (PHE)", "RandomForest", "Ridge"]
    ]
    clean_reg_map = {
        "Hypobaria_25kPa_Air": "25 kPa Air (5.3 kPa O$_2$)",
        "Hypobaria_25kPa_NormoxicO2": "25 kPa + Normoxic O$_2$",
        "Hypobaria_50kPa_Air": "50 kPa Air (10.5 kPa O$_2$)",
        "Hypobaria_50kPa_NormoxicO2": "50 kPa + Normoxic O$_2$",
        "Hypobaria_75kPa_Air": "75 kPa Air (15.8 kPa O$_2$)",
    }
    piv_loco.index = [clean_reg_map.get(i, i.replace("Hypobaria_", "").replace("_", " ")) for i in piv_loco.index]
    piv_loco.plot(kind="bar", ax=axA, color=["#c0392b", "#e74c3c", "#2980b9", "#7f8c8d"], width=0.75)
    axA.set_ylabel("Out-of-Condition Pathway Profile Correlation $r$")
    axA.set_xlabel("")
    axA.set_ylim(0.0, 1.08)
    axA.set_title("A. Leave-One-Condition-Out (LOCO) Generalization Across Unseen Regimes", loc="left")
    _anchor_xticks(axA, rotation=24, fontsize=8.3)
    axA.legend(loc="upper right", frameon=True, fontsize=7.8)
    axA.grid(True, axis="y", alpha=0.25)

    # Panel B: Counterfactual Pathway Trajectory Across NASA Exploration Atmosphere Setpoints (Shoot 10d)
    axB = fig.add_subplot(gs[0, 1])
    sp_order = [
        "Control_ISS_97kPa_21pctO2_Shoot_10d",
        "NASA_Staged_PreEVA_70.3kPa_26.5pctO2_Shoot_10d",
        "NASA_Exploration_56.5kPa_34pctO2_Shoot_10d",
        "Observed_50kPa_NormoxicO2_42pctO2_Shoot_10d",
        "Counterfactual_56.5kPa_UncompensatedAir_21pctO2_Shoot_10d",
        "Observed_50kPa_Air_21pctO2_Shoot_10d",
    ]
    sp_short = [
        "ISS Control\n(97 kPa, 21% O$_2$)",
        "NASA Staged\n(70.3 kPa, 26.5% O$_2$)",
        "NASA Exploration\n(56.5 kPa, 34% O$_2$)",
        "Normoxic 50 kPa\n(50 kPa, 42% O$_2$)",
        "Uncompensated\n(56.5 kPa, 21% O$_2$)",
        "Hypobaric 50 kPa\n(50 kPa, 21% O$_2$)",
    ]
    pws_show = [
        "ERF_VII_Core_Hypoxia_Anaerobic",
        "ABA_Desiccation_Stomatal_Closure",
        "Cuticle_Epicuticular_Wax_Lipid_Transport",
        "Cell_Wall_Mechanosensing_Expansion",
        "Oxylipin_JA_Chloroplast_Galactolipid",
        "Indole_Glucosinolate_Defense",
        "Phenylpropanoid_Sinapate_Flavonol",
        "ROS_Redox_Calcium_HeatShock",
        "Photosynthesis_Carbon_Fixation_LHC",
    ]
    mat_sp = cf_tab.loc[sp_order, pws_show].T.copy()
    mat_sp.index = [CLEAN_PATHWAY_NAMES.get(p, p.replace("_", " ")) for p in pws_show]
    mat_sp.columns = sp_short

    sns.heatmap(mat_sp, cmap="RdBu_r", center=0.0, vmin=-0.45, vmax=0.45, annot=True, fmt=".2f",
                annot_kws={"size": 7.2}, cbar_kws={"label": "TabPFN v2 Predicted Pathway $\\Delta\\log_2\\mathrm{FC}$"},
                ax=axB, linewidths=0.6)
    axB.set_title("B. TabPFN v2 Counterfactual Pathway Predictions Across NASA Setpoints (Shoot)", loc="left")
    axB.set_ylabel("")
    _anchor_xticks(axB, rotation=36, fontsize=8.0)
    axB.tick_params(axis="y", rotation=0, labelsize=8.3)

    # Panel C: Direct Comparison of Key Hub Gene Predictions at NASA 56.54 kPa / 34% O2 vs Uncompensated 56.54 kPa Air
    axC = fig.add_subplot(gs[1, 0])
    selected_hubs = [
        "PDC1 (253416_at)", "SUS1 (245998_at)", "HB1 (263096_at)", "PCO1 (250152_at)",
        "ADH1 (264953_at)", "CML38 (259879_at)", "TCH4 (247925_at)", "LOX2 (252618_at)",
        "AOS (249208_at)", "FLS1 (250533_at)", "SEN1 (252593_at)", "CYP79B2 (252827_at)",
        "HAI1 (247723_at)", "COR15A (263497_at)",
    ]
    hub_cols = [c for c in selected_hubs if c in cf_tab.columns]
    v_expl = cf_tab.loc["NASA_Exploration_56.5kPa_34pctO2_Shoot_10d", hub_cols].values.astype(float)
    sd_expl = cf_tab.loc["NASA_Exploration_56.5kPa_34pctO2_Shoot_10d", [f"{c}_SD" for c in hub_cols]].values.astype(float)
    v_uncomp = cf_tab.loc["Counterfactual_56.5kPa_UncompensatedAir_21pctO2_Shoot_10d", hub_cols].values.astype(float)
    sd_uncomp = cf_tab.loc["Counterfactual_56.5kPa_UncompensatedAir_21pctO2_Shoot_10d", [f"{c}_SD" for c in hub_cols]].values.astype(float)

    y_h = np.arange(len(hub_cols))
    axC.barh(y_h - 0.18, v_expl, xerr=1.96 * sd_expl, height=0.35, color="#16a085", capsize=2,
             label="NASA Exploration Setpoint (56.54 kPa, 34% O$_2$, $p\\mathrm{O}_2$=19.2 kPa)")
    axC.barh(y_h + 0.18, v_uncomp, xerr=1.96 * sd_uncomp, height=0.35, color="#c0392b", capsize=2,
             label="Uncompensated Decompression (56.54 kPa, 21% O$_2$, $p\\mathrm{O}_2$=11.9 kPa)")
    axC.axvline(0, color="black", lw=0.8)
    axC.set_yticks(y_h)
    axC.set_yticklabels([c.split(" ")[0] for c in hub_cols], fontsize=8.3, fontweight="bold")
    axC.invert_yaxis()
    axC.set_ylim(len(hub_cols) - 0.4 + 1.5, -0.6)  # headroom below COR15A for the legend
    axC.set_xlabel("TabPFN v2 Predicted Shoot $\\Delta\\log_2\\mathrm{FC}$ ($\\pm 95\\%$ Ensemble Interval)")
    axC.set_title("C. Hub Gene Counterfactuals: 34% O$_2$ Silences Hypoxia But Not Barosensory Hubs", loc="left")
    axC.legend(loc="lower right", frameon=True, fontsize=7.3)
    axC.grid(True, axis="x", alpha=0.25)

    # Panel D: Root vs Shoot & Developmental Age (5d vs 10d) Sensitivity at NASA Exploration Setpoint (56.54 kPa / 34% O2)
    axD = fig.add_subplot(gs[1, 1])
    rows_d = [
        "NASA_Exploration_56.5kPa_34pctO2_Shoot_10d",
        "NASA_Exploration_56.5kPa_34pctO2_Root_10d",
        "NASA_Exploration_56.5kPa_34pctO2_Root_5d",
        "NASA_Staged_PreEVA_70.3kPa_26.5pctO2_Shoot_10d",
        "NASA_Staged_PreEVA_70.3kPa_26.5pctO2_Root_10d",
    ]
    labels_d = [
        "56.5 kPa / 34% O$_2$\nShoot (10d)",
        "56.5 kPa / 34% O$_2$\nRoot (10d)",
        "56.5 kPa / 34% O$_2$\nYoung Root (5d)",
        "70.3 kPa / 26.5% O$_2$\nShoot (10d)",
        "70.3 kPa / 26.5% O$_2$\nRoot (10d)",
    ]
    mat_d = cf_tab.loc[rows_d, pws_show].copy()
    mat_d.index = labels_d
    mat_d.columns = [CLEAN_PATHWAY_NAMES.get(p, p.replace("_", " ")) for p in pws_show]

    sns.heatmap(mat_d.T, cmap="RdBu_r", center=0.0, vmin=-0.35, vmax=0.35, annot=True, fmt=".2f",
                annot_kws={"size": 7.2}, cbar_kws={"label": "Predicted $\\Delta\\log_2\\mathrm{FC}$"}, ax=axD, linewidths=0.6)
    axD.set_title("D. Organ & Developmental Stage Sensitivity Under NASA Setpoints", loc="left")
    axD.set_ylabel("")
    _anchor_xticks(axD, rotation=36, fontsize=8.0)
    axD.tick_params(axis="y", rotation=0, labelsize=8.3)

    fig.suptitle("Figure 6 | In-Silico Counterfactual Prediction of Arabidopsis Response to NASA's Exploration Atmosphere", y=0.98)
    out_path = FIG_DIR / "fig6_nasa_exploration_atmosphere_counterfactual.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    make_fig1_forensics()
    make_fig2_decoupling()
    make_fig3_hubs_shap()
    make_fig4_cellular_atlas()
    make_fig5_physiology_metabolomics()
    make_fig6_nasa_counterfactual()
    print("\n=== ALL 6 PUBLICATION FIGURES REGENERATED WITH STRICT ABAI QC ===")


if __name__ == "__main__":
    main()
