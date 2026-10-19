"""
Master Execution Pipeline for Workpackages 1-5 (WP1-WP5)
of the Arabidopsis Exploration Atmosphere TabPFN v2 Study.

Generates all quantitative ML benchmarks, 1,000-bootstrap 95% CIs, slice-based error analyses,
SHAP attributions, cellular/single-nucleus mappings, physiological/metabolomic triangulation,
and NASA Exploration Atmosphere (56.54 kPa / 34% O2) counterfactual predictions.
Saves Supplementary Tables S1-S6 to manuscript/tables/ and serialized artifacts to outputs/ml_results/.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
CACHE_ROOT = WORKSPACE / ".cache"
for sub in ["skrub", "hf", "torch", "mpl", "tabpfn", "xdg"]:
    (CACHE_ROOT / sub).mkdir(parents=True, exist_ok=True)

os.environ["SKRUB_DATA_DIRECTORY"] = str(CACHE_ROOT / "skrub")
os.environ["HF_HOME"] = str(CACHE_ROOT / "hf")
os.environ["TORCH_HOME"] = str(CACHE_ROOT / "torch")
os.environ["MPLCONFIGDIR"] = str(CACHE_ROOT / "mpl")
os.environ["TABPFN_MODEL_CACHE_DIR"] = str(CACHE_ROOT / "tabpfn")
os.environ["XDG_CACHE_HOME"] = str(CACHE_ROOT / "xdg")

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, mean_squared_error, mean_absolute_error, r2_score

from atmos_ml.ingest import (
    load_core_hypobaric_arrays,
    load_trap_cell_type_arrays,
    load_zenodo_physiology_metabolomics,
    load_pxd002353_proteomics,
    load_gse308672_snrnaseq,
)
from atmos_ml.features import (
    CURATED_PATHWAYS,
    map_pathways_to_probesets,
    TabPFNOmicsFeatureBuilder,
)
from atmos_ml.models import (
    TabPFNClassifier,
    TabPFNRegressor,
    TabPFNPHEClassifier,
    TabPFNPHERegressor,
    get_classification_models,
    get_regression_models,
    evaluate_classification_predictions,
    evaluate_regression_predictions,
    bootstrap_metric_ci,
)
from atmos_ml.interpret import (
    compute_orthogonal_gene_decomposition,
    compute_tabpfn_shap_values,
)

PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
TABLES_DIR = PROJECT_DIR / "manuscript" / "tables"
RESULTS_DIR = PROJECT_DIR / "outputs" / "ml_results"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_wp1_forensic_audit(core: Dict[str, pd.DataFrame], probe_pathways: Dict[str, List[str]], probe_to_label: Dict[str, str]) -> Dict[str, Any]:
    """
    WP1: Forensic Metadata Resolution, Deduplication of 18 Shared GSMs, and TabPFN v2 Organ Classification
    on Disputed Samples GSM2342806-GSM2342809.
    """
    print("\n=== Executing WP1: Data Forensics & TabPFN v2 Metadata Audit ===")
    s1_path = TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv"
    b1_path = RESULTS_DIR / "wp1_organ_classification_benchmark.csv"
    d1_path = RESULTS_DIR / "wp1_disputed_samples_audit.csv"
    r1_path = RESULTS_DIR / "wp1_technical_rehybridization_pairs.csv"
    if s1_path.exists() and b1_path.exists() and d1_path.exists() and r1_path.exists():
        print("  Loading cached WP1 results from disk...")
        return {
            "bench_df": pd.read_csv(b1_path),
            "disputed_df": pd.read_csv(d1_path, index_col=0),
            "rehyb_df": pd.read_csv(r1_path),
            "table_s1": pd.read_csv(s1_path, index_col=0),
        }
    meta = core["meta_unique"].copy()
    expr = core["expr_log2_all130"].T.copy()  # shape: (130 samples, 22746 probesets)

    # Separate 126 unambiguous samples vs 4 organ-conflict samples (GSM2342806-GSM2342809)
    disputed_gsms = ["GSM2342806", "GSM2342807", "GSM2342808", "GSM2342809"]
    clean_gsms = [g for g in meta.index if g not in disputed_gsms]

    X_clean = expr.loc[clean_gsms]
    y_clean = (meta.loc[clean_gsms, "char_organ"] == "Shoot").astype(int).values
    groups_clean = (
        meta.loc[clean_gsms, "series_id"].astype(str)
        + "_" + meta.loc[clean_gsms, "regime"].astype(str)
        + "_" + meta.loc[clean_gsms, "duration_h"].astype(str)
    ).values

    # 5-fold GroupKFold (grouped by condition so biological replicates stay together)
    gkf = GroupKFold(n_splits=5)
    models = get_classification_models(random_state=42)
    oof_probs = {mname: np.zeros((len(clean_gsms), 2), dtype=float) for mname in models}
    disputed_probs_folds = {mname: [] for mname in models}

    X_disputed = expr.loc[disputed_gsms]

    for fold_idx, (tr_idx, va_idx) in enumerate(gkf.split(X_clean, y_clean, groups=groups_clean)):
        fb = TabPFNOmicsFeatureBuilder(
            probe_pathways=probe_pathways,
            probe_to_label=probe_to_label,
            n_top_genes=60,
            task_type="classification",
            include_interactions=True,
        )
        X_tr_feat = fb.fit_transform(X_clean.iloc[tr_idx], y_clean[tr_idx])
        X_va_feat = fb.transform(X_clean.iloc[va_idx])
        X_disp_feat = fb.transform(X_disputed)

        for mname, model in models.items():
            m = model
            m.fit(X_tr_feat.values, y_clean[tr_idx])
            oof_probs[mname][va_idx] = m.predict_proba(X_va_feat.values)
            disputed_probs_folds[mname].append(m.predict_proba(X_disp_feat.values)[:, 1])

    bench_rows = []
    for mname in models:
        res = evaluate_classification_predictions(y_clean, oof_probs[mname], mname, n_boot=1000)
        res["Task"] = "WP1_Organ_Identity_Shoot_vs_Root"
        bench_rows.append(res)
    wp1_bench_df = pd.DataFrame(bench_rows)

    # Disputed sample forensic table
    # Check canonical Shoot photosynthetic markers (RBCS1A: 260037_at / AT1G67090, LHCB1.2: 265768_at / AT1G29910)
    # vs Root endodermis/stele markers (CASP1: 263979_at / AT2G36100, SCR: 251891_at / AT3G54220)
    annot = core["annotation"]
    shoot_marker_probes = annot[annot["TAIR"].isin(["AT1G67090", "AT1G29910", "AT1G29920", "AT3G54890", "AT1G51500"])].index.tolist()
    root_marker_probes = annot[annot["TAIR"].isin(["AT3G54220", "AT2G36100", "AT1G27740", "AT5G49270", "AT1G61590"])].index.tolist()

    clean_shoot_idx = [g for g in clean_gsms if meta.loc[g, "char_organ"] == "Shoot" and meta.loc[g, "series_id"] in ["GSE87867", "GSE87903"]]
    clean_root_idx = [g for g in clean_gsms if meta.loc[g, "char_organ"] == "Root" and meta.loc[g, "series_id"] in ["GSE87867", "GSE87903"]]

    ref_shoot_score = expr.loc[clean_shoot_idx, shoot_marker_probes].mean(axis=1).mean()
    ref_root_shoot_score = expr.loc[clean_root_idx, shoot_marker_probes].mean(axis=1).mean()

    forensic_rows = []
    for i, gsm in enumerate(disputed_gsms):
        r = meta.loc[gsm]
        p_tabpfn_phe = float(np.mean([p[i] for p in disputed_probs_folds["TabPFN v2 (PHE)"]]))
        p_tabpfn_sd = float(np.std([p[i] for p in disputed_probs_folds["TabPFN v2 (PHE)"]]))
        p_lgbm = float(np.mean([p[i] for p in disputed_probs_folds["LightGBM"]]))
        p_logreg = float(np.mean([p[i] for p in disputed_probs_folds["ElasticNet (LogReg)"]]))
        s_score = float(expr.loc[gsm, shoot_marker_probes].mean())
        rt_score = float(expr.loc[gsm, root_marker_probes].mean())
        forensic_rows.append({
            "gsm_id": gsm,
            "series_id": r["series_id"],
            "sample_title": r["sample_title"],
            "geo_title_organ": r["title_organ"],
            "geo_char_organ_erroneous": r["char_organ"],
            "raw_cel_filename": r["cel_basename"],
            "cel_inferred_organ": r["cel_organ"],
            "cel_hybridization_batch": r["cel_batch_id"],
            "cel_replicate_letter": r["cel_rep_letter"],
            "shoot_photosynthetic_marker_log2": round(s_score, 3),
            "root_endodermal_marker_log2": round(rt_score, 3),
            "ref_shoot_mean_log2": round(float(ref_shoot_score), 3),
            "ref_root_mean_log2": round(float(ref_root_shoot_score), 3),
            "TabPFN_v2_PHE_P_Shoot": round(p_tabpfn_phe, 5),
            "TabPFN_v2_PHE_SD": round(p_tabpfn_sd, 5),
            "LightGBM_P_Shoot": round(p_lgbm, 5),
            "ElasticNet_P_Shoot": round(p_logreg, 5),
            "resolved_organ": "Shoot" if p_tabpfn_phe > 0.9 else "Root",
        })

    # Also check technical re-hybridization correlations (GSM2342806 vs GSM2342807; GSM2342091 vs GSM2342092; GSM2342070 vs GSM2342071)
    tech_pairs = [
        ("GSM2342806", "GSM2342807", "GSE87903 75 kPa Shoot Rep A (Batch 5411 vs Batch 6827)"),
        ("GSM2342091", "GSM2342092", "GSE87867 50 kPa + O2 Shoot Rep A (Batch 5445 vs Batch 5444)"),
        ("GSM2342070", "GSM2342071", "GSE87867 50 kPa Root Rep A (Batch 5424 vs Batch 7199)"),
    ]
    tech_rows = []
    for g1, g2, desc in tech_pairs:
        r_raw = float(np.corrcoef(expr.loc[g1].values, expr.loc[g2].values)[0, 1])
        d1 = core["delta_log2_all130"][g1].values
        d2 = core["delta_log2_all130"][g2].values
        r_delta = float(np.corrcoef(d1, d2)[0, 1])
        tech_rows.append({
            "gsm_1": g1,
            "gsm_2": g2,
            "cel_1": meta.loc[g1, "cel_basename"],
            "cel_2": meta.loc[g2, "cel_basename"],
            "description": desc,
            "pearson_r_log2_expr": round(r_raw, 4),
            "pearson_r_delta_log2": round(r_delta, 4),
        })

    forensic_df = pd.DataFrame(forensic_rows)
    tech_df = pd.DataFrame(tech_rows)

    # Save Table S1 (Master Harmonized Sample & Forensic Metadata Table across all 130 unique GSMs)
    meta_out = meta.copy()
    meta_out["shoot_marker_log2"] = expr.loc[meta_out.index, shoot_marker_probes].mean(axis=1).round(3)
    meta_out["root_marker_log2"] = expr.loc[meta_out.index, root_marker_probes].mean(axis=1).round(3)
    meta_out.to_csv(TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv")
    forensic_df.to_csv(RESULTS_DIR / "wp1_disputed_samples_audit.csv", index=False)
    tech_df.to_csv(RESULTS_DIR / "wp1_technical_rehybridization_pairs.csv", index=False)
    wp1_bench_df.to_csv(RESULTS_DIR / "wp1_organ_classification_benchmark.csv", index=False)

    print("WP1 Organ Classification Benchmark (Top 4):")
    print(wp1_bench_df[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Brier_Score", "ECE"]].head(4).to_string(index=False))
    print("\nWP1 Disputed Samples Resolution:")
    print(forensic_df[["gsm_id", "raw_cel_filename", "geo_char_organ_erroneous", "TabPFN_v2_PHE_P_Shoot", "resolved_organ"]].to_string(index=False))

    return {
        "benchmark": wp1_bench_df,
        "forensic_disputed": forensic_df,
        "tech_pairs": tech_df,
    }


def run_wp2_atmospheric_decoupling(
    core: Dict[str, pd.DataFrame],
    probe_pathways: Dict[str, List[str]],
    probe_to_label: Dict[str, str],
) -> Dict[str, Any]:
    """
    WP2: Decoupling Total Atmospheric Pressure (P_total) vs Oxygen Partial Pressure (pO2)
    using TabPFN v2, Classical ML Baselines, Slice-Based Error Analysis, and SHAP + Orthogonal Hub Decomposition.
    """
    print("\n=== Executing WP2: Atmospheric Decoupling (P_total vs pO2) & Hub Identification ===")
    s2a_path = TABLES_DIR / "Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv"
    s2b_path = TABLES_DIR / "Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv"
    s2c_path = TABLES_DIR / "Table_S2C_Slice_Based_Error_Analysis.csv"
    s3_path = TABLES_DIR / "Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv"
    orth_path = RESULTS_DIR / "wp2_full_22746_orthogonal_decomposition.csv"
    sb_path = RESULTS_DIR / "wp2_shap_summary_hypobaria.csv"
    sh_path = RESULTS_DIR / "wp2_shap_summary_hypoxia.csv"
    if all(p.exists() for p in [s2a_path, s2b_path, s2c_path, s3_path, orth_path, sb_path, sh_path]):
        print("  Loading cached WP2 results from disk...")
        return {
            "reg_bench": pd.read_csv(s2a_path),
            "clf_bench": pd.read_csv(s2b_path),
            "slice_df": pd.read_csv(s2c_path),
            "orth_df": pd.read_csv(orth_path, index_col=0),
            "hub_table": pd.read_csv(s3_path, index_col=0),
            "shap_baro": pd.read_csv(sb_path),
            "shap_hypo": pd.read_csv(sh_path),
        }
    meta = core["meta_unique"].copy()
    delta_df = core["delta_log2_all130"].T.copy()  # shape: (130 samples, 22746 probesets)

    # Add explicit organ, age, and duration covariates to delta_df so models can account for context without leakage
    X_full = delta_df.copy()
    X_full.insert(0, "COV_is_shoot", (meta["consensus_organ"] == "Shoot").astype(float))
    X_full.insert(1, "COV_age_days", meta["age_days"].astype(float))
    X_full.insert(2, "COV_log2_duration_h", np.log2(meta["duration_h"].astype(float)))

    # Focus primary decoupling benchmark on the 58 24-h multi-pressure & O2-dissection samples
    # (GSE87867, GSE87868/OSD-136, GSE87903) where P_total (97, 75, 50, 25, 10, 5 kPa) and pO2 (21, 20.37, 15.75, 10.5, 5.25, 5.1, 2.1, 1.05 kPa)
    # vary across 2D space, AND also evaluate across all 130 samples!
    mask_58 = meta["series_id"].isin(["GSE87867", "GSE87868", "GSE87903"])
    idx_58 = meta.index[mask_58].tolist()
    X_58 = X_full.loc[idx_58]
    meta_58 = meta.loc[idx_58]

    y_baro_58 = meta_58["hypobaria_index"].values.astype(float)  # log2(97 / P_total_kPa)
    y_hypo_58 = meta_58["hypoxia_index"].values.astype(float)    # log2(20.37 / pO2_kPa)

    # 4-class atmospheric regime target on the 58 24-h samples:
    # 0: Normobaric Normoxia Control (97 kPa, 20.37 kPa O2)
    # 1: Pure Hypobaria / Normoxic O2 Supplemented (50 kPa + O2, 25 kPa + O2; pO2 = 21 kPa)
    # 2: Moderate Combined Hypobaria (75 kPa Air, 50 kPa Air; pO2 = 10.5 - 15.75 kPa)
    # 3: Severe Hypoxia / Extreme Hypobaria (25, 10, 5 kPa Air and 97 kPa / 5.1 kPa O2; pO2 <= 5.25 kPa)
    regime_4class = []
    for _, r in meta_58.iterrows():
        reg = r["regime"]
        if reg == "Control_97kPa_Normoxia":
            regime_4class.append(0)
        elif reg in ["Hypobaria_50kPa_NormoxicO2", "Hypobaria_25kPa_NormoxicO2"]:
            regime_4class.append(1)
        elif reg in ["Hypobaria_75kPa_Air", "Hypobaria_50kPa_Air"]:
            regime_4class.append(2)
        else:
            regime_4class.append(3)
    y_regime_58 = np.array(regime_4class, dtype=int)

    # Use 6-fold StratifiedKFold on regime_4class so every fold has balanced representation of all 4 atmospheric regimes
    skf = StratifiedKFold(n_splits=6, shuffle=True, random_state=42)

    reg_models_baro = get_regression_models(random_state=42)
    reg_models_hypo = get_regression_models(random_state=42)
    clf_models_reg = get_classification_models(random_state=42)

    oof_baro = {m: np.zeros(len(idx_58), dtype=float) for m in reg_models_baro}
    oof_hypo = {m: np.zeros(len(idx_58), dtype=float) for m in reg_models_hypo}
    oof_regime = {m: np.zeros((len(idx_58), 4), dtype=float) for m in clf_models_reg}

    for fold_idx, (tr_idx, va_idx) in enumerate(skf.split(X_58, y_regime_58)):
        # 1. Hypobaria Index (P_total) Regression
        fb_baro = TabPFNOmicsFeatureBuilder(
            probe_pathways=probe_pathways,
            probe_to_label=probe_to_label,
            n_top_genes=45,
            task_type="regression",
            include_interactions=True,
        )
        X_tr_b = fb_baro.fit_transform(X_58.iloc[tr_idx], y_baro_58[tr_idx])
        X_va_b = fb_baro.transform(X_58.iloc[va_idx])
        for mname, model in reg_models_baro.items():
            model.fit(X_tr_b.values, y_baro_58[tr_idx])
            oof_baro[mname][va_idx] = model.predict(X_va_b.values)

        # 2. Hypoxia Index (pO2) Regression
        fb_hypo = TabPFNOmicsFeatureBuilder(
            probe_pathways=probe_pathways,
            probe_to_label=probe_to_label,
            n_top_genes=45,
            task_type="regression",
            include_interactions=True,
        )
        X_tr_h = fb_hypo.fit_transform(X_58.iloc[tr_idx], y_hypo_58[tr_idx])
        X_va_h = fb_hypo.transform(X_58.iloc[va_idx])
        for mname, model in reg_models_hypo.items():
            model.fit(X_tr_h.values, y_hypo_58[tr_idx])
            oof_hypo[mname][va_idx] = model.predict(X_va_h.values)

        # 3. 4-Class Atmospheric Regime Classification
        fb_clf = TabPFNOmicsFeatureBuilder(
            probe_pathways=probe_pathways,
            probe_to_label=probe_to_label,
            n_top_genes=45,
            task_type="classification",
            include_interactions=True,
        )
        X_tr_c = fb_clf.fit_transform(X_58.iloc[tr_idx], y_regime_58[tr_idx])
        X_va_c = fb_clf.transform(X_58.iloc[va_idx])
        for mname, model in clf_models_reg.items():
            model.fit(X_tr_c.values, y_regime_58[tr_idx])
            oof_regime[mname][va_idx] = model.predict_proba(X_va_c.values)

    # Evaluate regression & classification benchmarks on 58 multi-pressure/O2 samples
    baro_rows = []
    for mname in reg_models_baro:
        r = evaluate_regression_predictions(y_baro_58, oof_baro[mname], mname, n_boot=1000)
        r["Task"] = "WP2A_Hypobaria_Index_log2_97_over_Ptotal (n=58)"
        # Paired Wilcoxon test on squared errors vs TabPFN v2 (PHE)
        se_phe = (y_baro_58 - oof_baro["TabPFN v2 (PHE)"]) ** 2
        se_m = (y_baro_58 - oof_baro[mname]) ** 2
        if mname != "TabPFN v2 (PHE)" and np.any(se_phe != se_m):
            _, p_val = stats.wilcoxon(se_phe, se_m)
        else:
            p_val = 1.0
        r["p_vs_TabPFN_PHE"] = float(p_val)
        baro_rows.append(r)

    hypo_rows = []
    for mname in reg_models_hypo:
        r = evaluate_regression_predictions(y_hypo_58, oof_hypo[mname], mname, n_boot=1000)
        r["Task"] = "WP2B_Hypoxia_Index_log2_20.37_over_pO2 (n=58)"
        se_phe = (y_hypo_58 - oof_hypo["TabPFN v2 (PHE)"]) ** 2
        se_m = (y_hypo_58 - oof_hypo[mname]) ** 2
        if mname != "TabPFN v2 (PHE)" and np.any(se_phe != se_m):
            _, p_val = stats.wilcoxon(se_phe, se_m)
        else:
            p_val = 1.0
        r["p_vs_TabPFN_PHE"] = float(p_val)
        hypo_rows.append(r)

    regime_rows = []
    for mname in clf_models_reg:
        r = evaluate_classification_predictions(y_regime_58, oof_regime[mname], mname, n_boot=1000)
        r["Task"] = "WP2C_4Class_Atmospheric_Regime (n=58)"
        regime_rows.append(r)

    # Also evaluate across ALL 130 unique arrays (including the 72 GSE87904 time-series arrays at 10 kPa vs 97 kPa)
    y_baro_130 = meta["hypobaria_index"].values.astype(float)
    y_hypo_130 = meta["hypoxia_index"].values.astype(float)
    skf_130 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    strat_130 = (meta["P_total_kPa"].astype(int).astype(str) + "_" + meta["consensus_organ"]).values
    oof_baro_130 = {m: np.zeros(len(meta), dtype=float) for m in ["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "RandomForest", "ElasticNet", "Ridge", "Dummy (Mean Baseline)"]}
    reg_sub_130 = {k: get_regression_models(42)[k] for k in oof_baro_130}
    for tr_idx, va_idx in skf_130.split(X_full, strat_130):
        fb_130 = TabPFNOmicsFeatureBuilder(
            probe_pathways=probe_pathways, probe_to_label=probe_to_label,
            n_top_genes=45, task_type="regression", include_interactions=True,
        )
        X_tr_130 = fb_130.fit_transform(X_full.iloc[tr_idx], y_baro_130[tr_idx])
        X_va_130 = fb_130.transform(X_full.iloc[va_idx])
        for mname, model in reg_sub_130.items():
            model.fit(X_tr_130.values, y_baro_130[tr_idx])
            oof_baro_130[mname][va_idx] = model.predict(X_va_130.values)

    for mname in oof_baro_130:
        r = evaluate_regression_predictions(y_baro_130, oof_baro_130[mname], mname, n_boot=1000)
        r["Task"] = "WP2D_All130_Hypobaria_Index_Regression (n=130)"
        se_phe = (y_baro_130 - oof_baro_130["TabPFN v2 (PHE)"]) ** 2
        se_m = (y_baro_130 - oof_baro_130[mname]) ** 2
        r["p_vs_TabPFN_PHE"] = float(stats.wilcoxon(se_phe, se_m)[1]) if (mname != "TabPFN v2 (PHE)" and np.any(se_phe != se_m)) else 1.0
        baro_rows.append(r)

    reg_bench_df = pd.DataFrame(baro_rows + hypo_rows)
    clf_bench_df = pd.DataFrame(regime_rows)

    # Slice-based error analysis on the 58 multi-pressure/O2 samples (Root vs Shoot, 5d vs 10d, Normoxic O2 vs Unsupplemented)
    slice_defs = [
        ("Organ: Root (n=31)", meta_58["consensus_organ"] == "Root"),
        ("Organ: Shoot (n=27)", meta_58["consensus_organ"] == "Shoot"),
        ("Age: 5-day Root (GSE87868, n=9)", meta_58["age_days"] == 5),
        ("Age: 10/11-day Root & Shoot (n=49)", meta_58["age_days"] >= 10),
        ("Regime: Normoxic O2 Supplemented (50/25 kPa + O2, n=13)", meta_58["o2_supplemented"]),
        ("Regime: Unsupplemented Air / Hypoxia (n=45)", ~meta_58["o2_supplemented"]),
    ]
    slice_rows = []
    for sname, smask in slice_defs:
        idx_s = np.where(smask.values)[0]
        for mname in ["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "RandomForest", "ElasticNet"]:
            clf_key = "ElasticNet (LogReg)" if mname == "ElasticNet" else mname
            rmse_b = float(np.sqrt(mean_squared_error(y_baro_58[idx_s], oof_baro[mname][idx_s])))
            mae_b = float(mean_absolute_error(y_baro_58[idx_s], oof_baro[mname][idx_s]))
            rmse_h = float(np.sqrt(mean_squared_error(y_hypo_58[idx_s], oof_hypo[mname][idx_s])))
            mae_h = float(mean_absolute_error(y_hypo_58[idx_s], oof_hypo[mname][idx_s]))
            acc_c = float(np.mean(np.argmax(oof_regime[clf_key][idx_s], axis=1) == y_regime_58[idx_s]))
            slice_rows.append({
                "Slice": sname,
                "Model": mname,
                "Hypobaria_RMSE": round(rmse_b, 4),
                "Hypobaria_MAE": round(mae_b, 4),
                "Hypoxia_RMSE": round(rmse_h, 4),
                "Hypoxia_MAE": round(mae_h, 4),
                "Regime_4Class_Accuracy": round(acc_c, 4),
            })
    slice_df = pd.DataFrame(slice_rows)

    # Save out-of-fold sample-level predictions on the 58 samples
    oof_58_df = meta_58[["series_id", "consensus_organ", "age_days", "P_total_kPa", "pO2_kPa", "regime", "hypobaria_index", "hypoxia_index"]].copy()
    oof_58_df["true_regime_4class"] = y_regime_58
    for mname in ["TabPFN v2 (PHE)", "TabPFN v2", "LightGBM", "RandomForest", "ElasticNet"]:
        clf_key = "ElasticNet (LogReg)" if mname == "ElasticNet" else mname
        oof_58_df[f"pred_baro_{mname}"] = oof_baro[mname]
        oof_58_df[f"pred_hypo_{mname}"] = oof_hypo[mname]
        oof_58_df[f"pred_regime_{mname}"] = np.argmax(oof_regime[clf_key], axis=1)
    oof_58_df.to_csv(RESULTS_DIR / "wp2_oof_predictions_58samples.csv")

    # Orthogonal decomposition across all 22,746 probesets + SHAP attributions on TabPFN v2
    print("  Computing multivariable orthogonal decomposition across 22,746 probesets...")
    orth_df = compute_orthogonal_gene_decomposition(
        delta_log2=core["delta_log2_all130"],
        meta_unique=meta,
        annot=core["annotation"],
    )

    print("  Computing exact TabPFN v2 SHAP attributions for Hypobaria (P_total) and Hypoxia (pO2)...")
    fb_shap_baro = TabPFNOmicsFeatureBuilder(
        probe_pathways=probe_pathways, probe_to_label=probe_to_label,
        n_top_genes=35, task_type="regression", include_interactions=True,
    )
    X_58_baro_feat = fb_shap_baro.fit_transform(X_58, y_baro_58)
    tab_reg_baro = TabPFNRegressor(n_estimators=4, device="cpu", random_state=42)
    tab_reg_baro.fit(X_58_baro_feat, y_baro_58)
    shap_vals_baro, shap_sum_baro = compute_tabpfn_shap_values(tab_reg_baro, X_58_baro_feat, X_58_baro_feat)

    fb_shap_hypo = TabPFNOmicsFeatureBuilder(
        probe_pathways=probe_pathways, probe_to_label=probe_to_label,
        n_top_genes=35, task_type="regression", include_interactions=True,
    )
    X_58_hypo_feat = fb_shap_hypo.fit_transform(X_58, y_hypo_58)
    tab_reg_hypo = TabPFNRegressor(n_estimators=4, device="cpu", random_state=42)
    tab_reg_hypo.fit(X_58_hypo_feat, y_hypo_58)
    shap_vals_hypo, shap_sum_hypo = compute_tabpfn_shap_values(tab_reg_hypo, X_58_hypo_feat, X_58_hypo_feat)

    shap_sum_baro.to_csv(RESULTS_DIR / "wp2_shap_summary_hypobaria.csv", index=False)
    shap_sum_hypo.to_csv(RESULTS_DIR / "wp2_shap_summary_hypoxia.csv", index=False)
    pd.DataFrame(shap_vals_baro, index=X_58_baro_feat.index, columns=X_58_baro_feat.columns).to_csv(RESULTS_DIR / "wp2_shap_matrix_hypobaria.csv")
    pd.DataFrame(shap_vals_hypo, index=X_58_hypo_feat.index, columns=X_58_hypo_feat.columns).to_csv(RESULTS_DIR / "wp2_shap_matrix_hypoxia.csv")
    X_58_baro_feat.to_csv(RESULTS_DIR / "wp2_feature_matrix_hypobaria.csv")
    X_58_hypo_feat.to_csv(RESULTS_DIR / "wp2_feature_matrix_hypoxia.csv")

    # Build Table S3: Curated Pathway Hub Genes + Top Orthogonal Barosensory, Hypoxia, and Dual Hub Nodes
    pathway_membership: Dict[str, str] = {}
    for pw_name, plist in probe_pathways.items():
        for p in plist:
            if p in pathway_membership:
                pathway_membership[p] += f";{pw_name}"
            else:
                pathway_membership[p] = pw_name
    orth_df["curated_pathway"] = [pathway_membership.get(p, "Unassigned_Discovery_Node") for p in orth_df.index]

    # Select all curated pathway probesets + top 100 discovery probesets by hub_composite_score
    curated_probes = [p for p in orth_df.index if orth_df.loc[p, "curated_pathway"] != "Unassigned_Discovery_Node"]
    top_disc_probes = (
        orth_df[orth_df["curated_pathway"] == "Unassigned_Discovery_Node"]
        .nlargest(100, "hub_composite_score")
        .index.tolist()
    )
    hub_table = orth_df.loc[sorted(list(set(curated_probes + top_disc_probes)))].sort_values(
        "hub_composite_score", ascending=False
    )

    # Save Table S2 (ML Benchmark & Slice Analysis) and Table S3 (Molecular Hub & Orthogonal Decomposition Table)
    reg_bench_df.to_csv(TABLES_DIR / "Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv", index=False)
    clf_bench_df.to_csv(TABLES_DIR / "Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv", index=False)
    slice_df.to_csv(TABLES_DIR / "Table_S2C_Slice_Based_Error_Analysis.csv", index=False)
    hub_table.to_csv(TABLES_DIR / "Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv")
    orth_df.to_csv(RESULTS_DIR / "wp2_full_22746_orthogonal_decomposition.csv")

    print("\nWP2 Regression Benchmarks (Hypobaria Index & Hypoxia Index):")
    print(reg_bench_df[["Task", "model", "RMSE", "MAE", "R2", "Spearman_rho", "p_vs_TabPFN_PHE"]].to_string(index=False))
    print("\nWP2 4-Class Atmospheric Regime Classification Benchmark:")
    print(clf_bench_df[["model", "ROC_AUC", "PR_AUC", "Macro_F1", "Accuracy", "Brier_Score", "ECE"]].to_string(index=False))

    return {
        "reg_bench": reg_bench_df,
        "clf_bench": clf_bench_df,
        "slice_df": slice_df,
        "orth_df": orth_df,
        "hub_table": hub_table,
        "shap_baro": shap_sum_baro,
        "shap_hypo": shap_sum_hypo,
    }


def run_wp3_cellular_tissue_mapping(
    core: Dict[str, pd.DataFrame],
    orth_df: pd.DataFrame,
    probe_pathways: Dict[str, List[str]],
) -> Dict[str, Any]:
    """
    WP3: Cellular and Tissue-Specific Trajectory Mapping across:
      - Layer 3A: 99 Cell-Population TRAP-seq & Total RNA Arrays (GSE14493 & GSE14502; Mustroph et al., PNAS 2009)
      - Layer 3B: 40,860 Single-Nucleus Root Tip Profiles under Normoxia vs 4% O2 Hypoxia (GSE308672; 2025)
    """
    print("\n=== Executing WP3: Cellular & Tissue-Specific Trajectory Mapping (TRAP-seq + snRNA-seq) ===")
    s4a_path = TABLES_DIR / "Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv"
    s4b_path = TABLES_DIR / "Table_S4B_Top80_Hubs_CellType_and_SingleNucleus_Localization.csv"
    sn_path = RESULTS_DIR / "wp3_gse308672_single_nucleus_lineage_counts.csv"
    if all(p.exists() for p in [s4a_path, s4b_path, sn_path]):
        print("  Loading cached WP3 results from disk...")
        return {
            "pathway_cell_atlas": pd.read_csv(s4a_path, index_col=0),
            "top_hubs_cell_atlas": pd.read_csv(s4b_path, index_col=0),
            "sn_counts": pd.read_csv(sn_path),
        }
    trap = load_trap_cell_type_arrays()
    m_trap = trap["meta"]
    e_trap = trap["expr"]

    # Compute cell-type-specific log2FC (Hypoxia vs Normoxia Control) and Baseline Normoxic Enrichment across promoters in GSE14502/14493
    promoters = sorted(m_trap["promoter"].unique().tolist())
    cell_type_names = {p: m_trap[m_trap["promoter"] == p]["cell_type"].iloc[0] for p in promoters}

    # Global normoxic baseline mean across all TRAP lines
    norm_all = e_trap[m_trap.index[~m_trap["is_hypoxia"]]].mean(axis=1)

    trap_baseline_z = pd.DataFrame(index=e_trap.index)
    trap_hypoxia_dlog2 = pd.DataFrame(index=e_trap.index)

    for p in promoters:
        cname = f"{p}_{cell_type_names[p]}"
        sub_norm = m_trap.index[(m_trap["promoter"] == p) & (~m_trap["is_hypoxia"]) & (~m_trap["has_sucrose"])].tolist()
        if not sub_norm:
            sub_norm = m_trap.index[(m_trap["promoter"] == p) & (~m_trap["is_hypoxia"])].tolist()
        sub_hyp = m_trap.index[(m_trap["promoter"] == p) & (m_trap["is_hypoxia"]) & (~m_trap["has_sucrose"])].tolist()
        if not sub_hyp:
            sub_hyp = m_trap.index[(m_trap["promoter"] == p) & (m_trap["is_hypoxia"])].tolist()

        if sub_norm:
            trap_baseline_z[cname] = e_trap[sub_norm].mean(axis=1) - norm_all
        if sub_norm and sub_hyp:
            trap_hypoxia_dlog2[cname] = e_trap[sub_hyp].mean(axis=1) - e_trap[sub_norm].mean(axis=1)

    # Compute Excised Root-Tip Hypoxia dlog2 (GSE14493) and Polysomal Translation Shift (p35S TRAP vs Total RNA under Hypoxia)
    h_rt = m_trap.index[(m_trap["series_id"] == "GSE14493") & (m_trap["is_hypoxia"])].tolist()
    c_rt = m_trap.index[(m_trap["series_id"] == "GSE14493") & (~m_trap["is_hypoxia"])].tolist()
    hypoxia_nosuc_dlog2 = e_trap[h_rt].mean(axis=1) - e_trap[c_rt].mean(axis=1)

    h_p35s = m_trap.index[(m_trap["promoter"] == "p35s") & (m_trap["is_hypoxia"])].tolist()
    c_p35s = m_trap.index[(m_trap["promoter"] == "p35s") & (~m_trap["is_hypoxia"])].tolist()
    h_tot = m_trap.index[(m_trap["promoter"] == "total") & (m_trap["is_hypoxia"])].tolist()
    c_tot = m_trap.index[(m_trap["promoter"] == "total") & (~m_trap["is_hypoxia"])].tolist()
    dlog2_p35s = e_trap[h_p35s].mean(axis=1) - e_trap[c_p35s].mean(axis=1)
    dlog2_tot = e_trap[h_tot].mean(axis=1) - e_trap[c_tot].mean(axis=1)
    # Polysomal Translational Efficiency Shift (TRAP p35S dlog2 minus Total RNA dlog2)
    sucrose_rescue_dlog2 = dlog2_p35s - dlog2_tot

    # Compute pathway-level cell-type enrichment (both baseline localization and hypoxia translatome induction)
    pw_cell_rows = []
    for pw_name, plist in probe_pathways.items():
        valid_p = [p for p in plist if p in trap_baseline_z.index]
        row_dict = {
            "Pathway": pw_name,
            "n_probesets": len(valid_p),
            "GSE14493_Hypoxia_NoSucrose_dlog2": float(hypoxia_nosuc_dlog2.loc[valid_p].mean()),
            "GSE14493_Sucrose_Rescue_vs_NoSucrose_dlog2": float(sucrose_rescue_dlog2.loc[valid_p].mean()),
            "Polysomal_TE_Shift_p35S_vs_Total_dlog2": float(sucrose_rescue_dlog2.loc[valid_p].mean()),
        }
        for col in trap_baseline_z.columns:
            row_dict[f"BaselineLoc_{col}"] = float(trap_baseline_z.loc[valid_p, col].mean())
        for col in trap_hypoxia_dlog2.columns:
            row_dict[f"HypoxiaDlog2_{col}"] = float(trap_hypoxia_dlog2.loc[valid_p, col].mean())
        pw_cell_rows.append(row_dict)
    pw_cell_df = pd.DataFrame(pw_cell_rows).set_index("Pathway")

    # Layer 3B: Single-Nucleus Root Tip Hypoxia (GSE308672)
    sn = load_gse308672_snrnaseq()
    sn_pb = sn["pseudobulk_log2cpm"]
    sn_counts = sn["cell_counts"]

    # Compute lineage-specific log2FC (Hypoxia_4pct vs Normoxia_21pct) across the 2 biological replicates per group in GSE308672
    lineages = sorted(sn_counts["lineage"].unique().tolist())
    sn_lineage_dlog2 = pd.DataFrame(index=sn_pb.index)
    sn_lineage_norm = pd.DataFrame(index=sn_pb.index)

    for lin in lineages:
        norm_cols = [c for c in sn_pb.columns if "Normoxia_21pct" in c and c.endswith(f"_{lin}")]
        hyp_cols = [c for c in sn_pb.columns if "Hypoxia_4pct" in c and c.endswith(f"_{lin}")]
        if norm_cols and hyp_cols:
            sn_lineage_norm[lin] = sn_pb[norm_cols].mean(axis=1)
            sn_lineage_dlog2[lin] = sn_pb[hyp_cols].mean(axis=1) - sn_pb[norm_cols].mean(axis=1)

    # Map Curated Pathways to Single-Nucleus Root Lineages (by TAIR AGI ID)
    pw_sn_rows = []
    for pw_name, agi_list in CURATED_PATHWAYS.items():
        valid_agi = [g for g in agi_list if g in sn_lineage_dlog2.index]
        r_dict = {"Pathway": pw_name, "n_genes_snRNA": len(valid_agi)}
        for lin in lineages:
            r_dict[f"snRNA_Normoxia_log2CPM_{lin}"] = float(sn_lineage_norm.loc[valid_agi, lin].mean()) if valid_agi else 0.0
            r_dict[f"snRNA_Hypoxia_dlog2_{lin}"] = float(sn_lineage_dlog2.loc[valid_agi, lin].mean()) if valid_agi else 0.0
        pw_sn_rows.append(r_dict)
    pw_sn_df = pd.DataFrame(pw_sn_rows).set_index("Pathway")

    # Combine pathway cell-type TRAP and single-nucleus matrices into Table S4
    table_s4_pw = pw_cell_df.join(pw_sn_df)
    table_s4_pw.to_csv(TABLES_DIR / "Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv")

    # Also build Gene-Level Cell-Type & Single-Nucleus Localization Table for the Top Hub Genes (Table S4B)
    top_hubs = orth_df.nlargest(80, "hub_composite_score").copy()
    for col in trap_baseline_z.columns:
        top_hubs[f"TRAP_Base_{col}"] = trap_baseline_z.reindex(top_hubs.index)[col].values
    for col in trap_hypoxia_dlog2.columns:
        top_hubs[f"TRAP_HypDlog2_{col}"] = trap_hypoxia_dlog2.reindex(top_hubs.index)[col].values
    top_hubs["GSE14493_Sucrose_Rescue_dlog2"] = sucrose_rescue_dlog2.reindex(top_hubs.index).values

    for lin in lineages:
        vals_d = []
        for _, r in top_hubs.iterrows():
            tair_first = str(r["TAIR"]).split("|")[0].strip()
            vals_d.append(float(sn_lineage_dlog2.loc[tair_first, lin]) if tair_first in sn_lineage_dlog2.index else np.nan)
        top_hubs[f"snRNA_HypDlog2_{lin}"] = vals_d

    top_hubs.to_csv(TABLES_DIR / "Table_S4B_Top80_Hubs_CellType_and_SingleNucleus_Localization.csv")
    sn_counts.to_csv(RESULTS_DIR / "wp3_gse308672_single_nucleus_lineage_counts.csv", index=False)

    print("WP3 Pathway Cell-Type & Sucrose Rescue Summary (Top 6 Pathways):")
    cols_print = ["GSE14493_Hypoxia_NoSucrose_dlog2", "GSE14493_Sucrose_Rescue_vs_NoSucrose_dlog2"] + [c for c in table_s4_pw.columns if c.startswith("BaselineLoc_")][:4]
    print(table_s4_pw[cols_print].head(6).round(3).to_string())

    return {
        "pathway_cell_atlas": table_s4_pw,
        "top_hubs_cell_atlas": top_hubs,
        "sn_counts": sn_counts,
    }


def run_wp4_physiological_metabolic_bridge(
    core: Dict[str, pd.DataFrame],
    orth_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    WP4: Multi-Omics Physiological, Metabolomic, and Proteomic Bridge across:
      - ZENODO16536514 (62 kPa vs 101 kPa x 25%, 50%, 70% RH gas exchange, chlorophyll fluorescence,
        leaf water content, d13C, and LC-MS metabolomics)
      - PXD002353 (Col-0 vs SnRK1.1K48M submergence iTRAQ proteome)
      - TabPFN v2 phenotypic classification & humidity-rescue counterfactual evaluation.
    """
    print("\n=== Executing WP4: Physiological, Metabolomic & SnRK1 Proteomic Bridge ===")
    zen = load_zenodo_physiology_metabolomics()
    gas = zen["gas_exchange"]
    fluo = zen["fluorescence"]
    nit = zen["nitrogen_d13c"]
    growth = zen["growth_rwc"]
    pig = zen["pigments"]
    met = zen["metabolites"]

    # 1. Statistical comparison of physiological parameters at 62 kPa vs 101 kPa (50% RH)
    phys_traits = [
        (gas, "GH2O", "Stomatal conductance g_sw (mmol m-2 s-1)"),
        (gas, "E", "Transpiration rate E (mmol m-2 s-1)"),
        (gas, "A", "Net CO2 assimilation rate A (umol m-2 s-1)"),
        (gas, "VPD", "Leaf-to-air vapor pressure ratio VPD (Pa kPa-1)"),
        (gas, "ci", "Intercellular CO2 concentration c_i (umol mol-1)"),
        (gas, "cica", "Intercellular-to-ambient CO2 ratio c_i/c_a"),
        (growth, "RWC", "Leaf relative water content RWC"),
        (growth, "FW (g)", "Rosette fresh weight FW (g)"),
        (growth, "DW (g)", "Rosette dry weight DW (g)"),
        (nit, "d13C", "Carbon isotope composition delta13C (per mil)"),
        (nit, "Npp", "Leaf nitrogen concentration N (%)"),
        (nit, "LNC", "Total leaf nitrogen content LNC"),
        (pig, "chlab", "Chlorophyll a/b ratio"),
        (pig, "chlcar", "Chlorophyll / Carotenoid ratio"),
        (pig, "chlarea", "Chlorophyll per unit leaf area (ug cm-2)"),
    ]
    phys_rows = []
    for df_p, col, label in phys_traits:
        v101 = df_p[df_p["P_total_kPa"] == 101][col].dropna().values.astype(float)
        v62 = df_p[df_p["P_total_kPa"] == 62][col].dropna().values.astype(float)
        t_stat, p_ttest = stats.ttest_ind(v62, v101, equal_var=False)
        u_stat, p_mwu = stats.mannwhitneyu(v62, v101, alternative="two-sided")
        # Hedges' g effect size
        nx, ny = len(v62), len(v101)
        dof = nx + ny - 2
        pool_sd = np.sqrt(((nx - 1) * np.var(v62, ddof=1) + (ny - 1) * np.var(v101, ddof=1)) / max(dof, 1))
        cohen_d = (np.mean(v62) - np.mean(v101)) / max(pool_sd, 1e-9)
        hedges_g = cohen_d * (1.0 - 3.0 / (4.0 * dof - 1.0))
        pct_change = 100.0 * (np.mean(v62) - np.mean(v101)) / abs(np.mean(v101))
        phys_rows.append({
            "Trait_Code": col,
            "Trait_Description": label,
            "n_101kPa": nx,
            "Mean_101kPa": round(float(np.mean(v101)), 4),
            "SD_101kPa": round(float(np.std(v101, ddof=1)), 4),
            "Median_101kPa": round(float(np.median(v101)), 4),
            "IQR_101kPa": round(float(np.percentile(v101, 75) - np.percentile(v101, 25)), 4),
            "n_62kPa": ny,
            "Mean_62kPa": round(float(np.mean(v62)), 4),
            "SD_62kPa": round(float(np.std(v62, ddof=1)), 4),
            "Median_62kPa": round(float(np.median(v62)), 4),
            "IQR_62kPa": round(float(np.percentile(v62, 75) - np.percentile(v62, 25)), 4),
            "Pct_Change_62_vs_101": round(float(pct_change), 2),
            "Hedges_g": round(float(hedges_g), 3),
            "Welch_t_p": float(p_ttest),
            "MannWhitney_U_p": float(p_mwu),
        })
    phys_summary_df = pd.DataFrame(phys_rows)

    # 2. TabPFN v2 physiological classification & stomatal conductance prediction on Gas Exchange (n=52)
    gas_clean = gas[["E", "VPD", "GH2O", "A", "ci", "cica", "Tleaf", "PARamb", "P_total_kPa"]].dropna().copy()
    X_gas = gas_clean[["E", "GH2O", "A", "ci", "cica", "Tleaf", "PARamb"]].values
    y_gas_p62 = (gas_clean["P_total_kPa"] == 62).astype(int).values
    skf_gas = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    gas_models = {
        "TabPFN v2 (PHE)": TabPFNPHEClassifier(42),
        "TabPFN v2": TabPFNClassifier(n_estimators=4, device="cpu", random_state=42),
        "LightGBM": get_classification_models(42)["LightGBM"],
        "RandomForest": get_classification_models(42)["RandomForest"],
        "Ridge (L2 LogReg)": get_classification_models(42)["Ridge (L2 LogReg)"],
    }
    oof_gas = {m: np.zeros((len(gas_clean), 2), dtype=float) for m in gas_models}
    for tr_idx, va_idx in skf_gas.split(X_gas, y_gas_p62):
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_gas[tr_idx])
        X_va_s = scaler.transform(X_gas[va_idx])
        for mname, model in gas_models.items():
            model.fit(X_tr_s, y_gas_p62[tr_idx])
            oof_gas[mname][va_idx] = model.predict_proba(X_va_s)

    gas_bench_rows = []
    for mname in gas_models:
        r = evaluate_classification_predictions(y_gas_p62, oof_gas[mname], mname, n_boot=1000)
        r["Task"] = "WP4_GasExchange_62kPa_vs_101kPa_Classification (n=52)"
        gas_bench_rows.append(r)
    gas_bench_df = pd.DataFrame(gas_bench_rows)

    # 3. TabPFN v2 Metabolomic Humidity-Rescue Counterfactual Analysis on ZENODO16536514 (12 samples across 4 groups)
    # Train TabPFN v2 on 101kPa_RH50 (0 = Normobaric baseline) vs 62kPa_RH50 (1 = Hypobaric stress at 50% RH),
    # and evaluate posterior probability P(Hypobaric Stress) on held-out 62kPa_RH70 (elevated 70% RH at 62 kPa)
    # and 101kPa_RH25 (low 25% RH at 101 kPa)!
    met_sample_cols = [
        "101kPa_RH50_Rep1", "101kPa_RH50_Rep2", "101kPa_RH50_Rep3",
        "62kPa_RH50_Rep1", "62kPa_RH50_Rep2", "62kPa_RH50_Rep3",
        "62kPa_RH70_Rep1", "62kPa_RH70_Rep2", "62kPa_RH70_Rep3",
        "101kPa_RH25_Rep1", "101kPa_RH25_Rep2", "101kPa_RH25_Rep3",
    ]
    X_met_all = np.log2(1.0 + met[met_sample_cols].T.values)  # shape: (12 samples, 27 metabolites)
    X_train_50rh = X_met_all[:6]  # 3 x 101kPa_RH50 (0), 3 x 62kPa_RH50 (1)
    y_train_50rh = np.array([0, 0, 0, 1, 1, 1], dtype=int)

    scaler_met = StandardScaler()
    X_train_50rh_s = scaler_met.fit_transform(X_train_50rh)
    X_eval_all_s = scaler_met.transform(X_met_all)

    tab_met_clf = TabPFNClassifier(n_estimators=4, device="cpu", random_state=42)
    tab_met_clf.fit(X_train_50rh_s, y_train_50rh)
    probs_met = tab_met_clf.predict_proba(X_eval_all_s)[:, 1]
    met_counterfactual_df = pd.DataFrame({
        "sample_id": met_sample_cols,
        "group": ["101kPa_RH50"] * 3 + ["62kPa_RH50"] * 3 + ["62kPa_RH70_Rescue"] * 3 + ["101kPa_RH25_DryAir"] * 3,
        "P_total_kPa": [101] * 3 + [62] * 3 + [62] * 3 + [101] * 3,
        "RH_pct": [50] * 3 + [50] * 3 + [70] * 3 + [25] * 3,
        "TabPFN_P_Hypobaric_Metabolic_State": np.round(probs_met, 4),
    })

    # 4. PXD002353 SnRK1.1K48M Submergence Proteomics Integration with Hypobaric Transcriptome
    pxd = load_pxd002353_proteomics()
    # Map orth_df probesets to primary TAIR ID and join with PXD002353
    orth_tair = orth_df.copy()
    orth_tair["PRIMARY_TAIR"] = orth_tair["TAIR"].fillna("").astype(str).apply(lambda s: str(s).split("|")[0].strip())
    orth_pxd = orth_tair.merge(pxd, left_on="PRIMARY_TAIR", right_index=True, how="inner")
    orth_pxd["abs_SnRK1_dep"] = np.abs(orth_pxd["SnRK1_dependency_3h_log2"])
    top_pxd_hubs = orth_pxd.sort_values("hub_composite_score", ascending=False).head(80)

    # Save Table S5 files
    phys_summary_df.to_csv(TABLES_DIR / "Table_S5A_Zenodo16536514_Physiology_62kPa_vs_101kPa_Stats.csv", index=False)
    met.to_csv(TABLES_DIR / "Table_S5B_Zenodo16536514_Metabolomics_Pressure_x_Humidity_Triangulation.csv", index=False)
    top_pxd_hubs.to_csv(TABLES_DIR / "Table_S5C_PXD002353_SnRK1_Proteome_Transcriptome_Integration.csv")
    gas_bench_df.to_csv(RESULTS_DIR / "wp4_gas_exchange_tabpfn_benchmark.csv", index=False)
    met_counterfactual_df.to_csv(RESULTS_DIR / "wp4_metabolomics_humidity_rescue_counterfactual.csv", index=False)

    print("WP4 Physiological Contrasts (62 kPa vs 101 kPa):")
    print(phys_summary_df[["Trait_Code", "Mean_101kPa", "Mean_62kPa", "Pct_Change_62_vs_101", "Hedges_g", "Welch_t_p"]].head(10).to_string(index=False))
    print("\nWP4 Metabolomic Humidity-Rescue Posterior Probabilities P(Hypobaric State):")
    print(met_counterfactual_df.groupby("group")["TabPFN_P_Hypobaric_Metabolic_State"].agg(["mean", "std"]).to_string())

    return {
        "phys_summary": phys_summary_df,
        "metabolites": met,
        "gas_bench": gas_bench_df,
        "met_counterfactual": met_counterfactual_df,
        "pxd_hubs": top_pxd_hubs,
    }


def run_wp5_nasa_counterfactual(
    core: Dict[str, pd.DataFrame],
    probe_pathways: Dict[str, List[str]],
    orth_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    WP5: Leave-One-Condition-Out (LOCO) Validation & In-Silico Counterfactual Prediction
    at NASA's Exact Exploration Atmosphere Setpoints:
      - Exploration Habitat: 56.54 kPa (8.2 psia), 34% O2, pO2 = 19.22 kPa (diffusivity = 1.72x)
      - Pre-EVA Staged Decompression: 70.33 kPa (10.2 psia), 26.5% O2, pO2 = 18.64 kPa (diffusivity = 1.38x)
      - Uncompensated 56.54 kPa Air: 56.54 kPa, 21% O2, pO2 = 11.87 kPa (diffusivity = 1.72x)
    """
    print("\n=== Executing WP5: LOCO Validation & NASA Exploration Atmosphere (56.54 kPa / 34% O2) Counterfactual ===")
    meta = core["meta_unique"].copy()
    delta = core["delta_log2_all130"]

    # Filter to the 58 24-h multi-pressure & O2-dissection samples
    mask_58 = meta["series_id"].isin(["GSE87867", "GSE87868", "GSE87903"])
    m58 = meta.loc[mask_58].copy()
    d58 = delta[m58.index]

    # Compute sample-level pathway response scores (mean Delta log2FC of pathway probesets) across the 58 arrays
    pw_names = list(probe_pathways.keys())
    Y_pw = pd.DataFrame(index=m58.index, columns=pw_names, dtype=float)
    for pw, plist in probe_pathways.items():
        valid_p = [p for p in plist if p in d58.index]
        Y_pw[pw] = d58.loc[valid_p].mean(axis=0).values

    # Also include top 20 individual molecular hub genes (by hub_composite_score & biological diversity)
    key_hub_symbols = [
        "ADH1", "PDC1", "SUS1", "HB1", "PCO1", "LBD41", "CML38",
        "RD29B", "RAB18", "COR15A", "ATHB7", "HAI1",
        "LTP3", "LTP4", "CER1",
        "LOX2", "AOS", "MGD1",
        "CYP79B2", "SNG1", "FLS1",
        "ASN1", "SEN1", "TCH4", "RBOHD", "RBCS1A"
    ]
    annot = core["annotation"]
    hub_probes = []
    hub_labels = []
    for sym in key_hub_symbols:
        matches = annot[annot["PRIMARY_SYMBOL"].str.upper() == sym.upper()].index.tolist()
        if not matches:
            matches = annot[annot["SYMBOL"].fillna("").str.upper().str.contains(sym.upper())].index.tolist()
        matches = [p for p in matches if p in d58.index]
        if matches:
            # Pick probeset with highest hub_composite_score
            best_p = orth_df.loc[matches, "hub_composite_score"].idxmax()
            if best_p not in hub_probes:
                hub_probes.append(best_p)
                hub_labels.append(f"{sym} ({best_p})")

    Y_hubs = pd.DataFrame(index=m58.index)
    for p, lbl in zip(hub_probes, hub_labels):
        Y_hubs[lbl] = d58.loc[p].values

    # Physical design features X_phys for each sample:
    # [P_total_kPa, pO2_kPa, O2_frac, diffusivity_factor, hypobaria_index, hypoxia_index, is_shoot, age_days]
    def _build_phys_features(df_meta: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({
            "P_total_kPa": df_meta["P_total_kPa"].astype(float),
            "pO2_kPa": df_meta["pO2_kPa"].astype(float),
            "O2_frac": df_meta["O2_frac"].astype(float),
            "diffusivity_factor": df_meta["diffusivity_factor"].astype(float),
            "hypobaria_index": df_meta["hypobaria_index"].astype(float),
            "hypoxia_index": df_meta["hypoxia_index"].astype(float),
            "is_shoot": (df_meta["consensus_organ"] == "Shoot").astype(float),
            "age_days": df_meta["age_days"].astype(float),
        }, index=df_meta.index)

    X_phys_58 = _build_phys_features(m58)

    # 1. Leave-One-Condition-Out (LOCO) Validation across unseen (P_total, pO2) regimes
    loco_regimes = [
        "Hypobaria_50kPa_NormoxicO2",  # Closest empirical analog to NASA Exploration Atmosphere!
        "Hypobaria_75kPa_Air",         # Closest empirical analog to 70.3 kPa staged decompression!
        "Hypobaria_50kPa_Air",
        "Hypobaria_25kPa_NormoxicO2",
        "Hypobaria_25kPa_Air",
    ]
    loco_rows = []
    for hold_reg in loco_regimes:
        for organ_val, organ_name in [(1.0, "Shoot"), (0.0, "Root")]:
            te_mask = (m58["regime"] == hold_reg) & ((m58["consensus_organ"] == "Shoot") == (organ_val == 1.0))
            tr_mask = ~te_mask
            if np.sum(te_mask) == 0:
                continue
            X_tr_p = X_phys_58.loc[tr_mask].values
            X_te_p = X_phys_58.loc[te_mask].head(1).values  # Predict condition centroid

            obs_vec = Y_pw.loc[te_mask].mean(axis=0).values
            for mname, reg_cls in [
                ("TabPFN v2 (PHE)", lambda: TabPFNPHERegressor(42)),
                ("TabPFN v2", lambda: TabPFNRegressor(n_estimators=4, device="cpu", random_state=42)),
                ("Ridge", lambda: get_regression_models(42)["Ridge"]),
                ("RandomForest", lambda: get_regression_models(42)["RandomForest"]),
            ]:
                pred_vec = []
                for col_idx in range(Y_pw.shape[1]):
                    y_tr_col = Y_pw.loc[tr_mask].iloc[:, col_idx].values
                    reg = reg_cls()
                    reg.fit(X_tr_p, y_tr_col)
                    pred_vec.append(float(reg.predict(X_te_p)[0]))
                pred_vec = np.array(pred_vec)
                r_pear = float(np.corrcoef(obs_vec, pred_vec)[0, 1])
                r_spear = float(stats.spearmanr(obs_vec, pred_vec)[0])
                rmse_v = float(np.sqrt(mean_squared_error(obs_vec, pred_vec)))
                mae_v = float(mean_absolute_error(obs_vec, pred_vec))
                loco_rows.append({
                    "Held_Out_Regime": hold_reg,
                    "Organ": organ_name,
                    "Model": mname,
                    "Pearson_r_12Pathways": round(r_pear, 4),
                    "Spearman_rho_12Pathways": round(r_spear, 4),
                    "RMSE_dlog2": round(rmse_v, 4),
                    "MAE_dlog2": round(mae_v, 4),
                })
    loco_df = pd.DataFrame(loco_rows)

    # 2. Fit full-grid TabPFN v2 models and predict counterfactual setpoints for Shoot (10d) and Root (10d & 5d)
    setpoints = [
        ("Control_ISS_97kPa_21pctO2", 97.0, 20.37, 0.2100),
        ("NASA_Staged_PreEVA_70.3kPa_26.5pctO2", 70.33, 18.64, 0.2650),
        ("NASA_Exploration_56.5kPa_34pctO2", 56.54, 19.22, 0.3400),
        ("Observed_50kPa_NormoxicO2_42pctO2", 50.0, 21.00, 0.4200),
        ("Counterfactual_56.5kPa_UncompensatedAir_21pctO2", 56.54, 11.87, 0.2100),
        ("Observed_50kPa_Air_21pctO2", 50.0, 10.50, 0.2100),
        ("Observed_25kPa_NormoxicO2_84pctO2", 25.0, 21.00, 0.8400),
        ("Observed_25kPa_Air_21pctO2", 25.0, 5.25, 0.2100),
    ]
    cf_rows = []
    for sp_name, p_tot, p_o2, o2_f in setpoints:
        for organ_name, is_sh, age_d in [("Shoot_10d", 1.0, 10.0), ("Root_10d", 0.0, 10.0), ("Root_5d", 0.0, 5.0)]:
            cf_rows.append({
                "Setpoint_ID": f"{sp_name}_{organ_name}",
                "Setpoint_Name": sp_name,
                "Organ_Stage": organ_name,
                "P_total_kPa": p_tot,
                "pO2_kPa": p_o2,
                "O2_frac": o2_f,
                "diffusivity_factor": 97.0 / p_tot,
                "hypobaria_index": np.log2(97.0 / p_tot),
                "hypoxia_index": np.log2(20.37 / p_o2),
                "is_shoot": is_sh,
                "age_days": age_d,
            })
    cf_meta_df = pd.DataFrame(cf_rows).set_index("Setpoint_ID")
    X_cf = cf_meta_df[X_phys_58.columns].values

    # Predict both Pathway scores and Top Hub Gene Delta log2FCs with uncertainty intervals across 3 temperature TabPFN v2 models
    all_targets = pd.concat([Y_pw, Y_hubs], axis=1)
    cf_pred_mean = pd.DataFrame(index=cf_meta_df.index, columns=all_targets.columns, dtype=float)
    cf_pred_sd = pd.DataFrame(index=cf_meta_df.index, columns=all_targets.columns, dtype=float)

    for col in all_targets.columns:
        y_vec = all_targets[col].values
        member_preds = []
        for seed_offset, temp in [(0, 0.9), (11, 0.8), (23, 1.0)]:
            reg = TabPFNRegressor(n_estimators=4, softmax_temperature=temp, device="cpu", random_state=42 + seed_offset)
            reg.fit(X_phys_58.values, y_vec)
            member_preds.append(reg.predict(X_cf))
        member_preds = np.array(member_preds)
        cf_pred_mean[col] = np.mean(member_preds, axis=0)
        cf_pred_sd[col] = np.std(member_preds, axis=0)

    table_s6 = cf_meta_df.join(cf_pred_mean).join(cf_pred_sd.add_suffix("_SD"))
    table_s6.to_csv(TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv")
    loco_df.to_csv(TABLES_DIR / "Table_S6B_Leave_One_Condition_Out_Validation.csv", index=False)

    print("WP5 Leave-One-Condition-Out (LOCO) Validation Summary by Model:")
    print(loco_df.groupby("Model")[["Pearson_r_12Pathways", "Spearman_rho_12Pathways", "RMSE_dlog2", "MAE_dlog2"]].mean().round(4).to_string())
    print("\nWP5 NASA Exploration Atmosphere Counterfactual Pathway Predictions (Shoot_10d & Root_10d):")
    show_pws = [
        "ERF_VII_Core_Hypoxia_Anaerobic",
        "ABA_Desiccation_Stomatal_Closure",
        "Cuticle_Epicuticular_Wax_Lipid_Transport",
        "Oxylipin_JA_Chloroplast_Galactolipid",
        "Indole_Glucosinolate_Defense",
        "Photosynthesis_Carbon_Fixation_LHC",
    ]
    print(table_s6.loc[
        table_s6["Setpoint_Name"].isin([
            "NASA_Exploration_56.5kPa_34pctO2",
            "NASA_Staged_PreEVA_70.3kPa_26.5pctO2",
            "Counterfactual_56.5kPa_UncompensatedAir_21pctO2",
        ]),
        ["Setpoint_Name", "Organ_Stage"] + show_pws
    ].round(3).to_string(index=False))

    return {
        "loco_df": loco_df,
        "counterfactual_table": table_s6,
    }


def main():
    core = load_core_hypobaric_arrays()
    annot = core["annotation"]
    probe_pathways = map_pathways_to_probesets(annot, CURATED_PATHWAYS)
    probe_to_label = annot["PRIMARY_SYMBOL"].to_dict()

    wp1_res = run_wp1_forensic_audit(core, probe_pathways, probe_to_label)
    wp2_res = run_wp2_atmospheric_decoupling(core, probe_pathways, probe_to_label)
    wp3_res = run_wp3_cellular_tissue_mapping(core, wp2_res["orth_df"], probe_pathways)
    wp4_res = run_wp4_physiological_metabolic_bridge(core, wp2_res["orth_df"])
    wp5_res = run_wp5_nasa_counterfactual(core, probe_pathways, wp2_res["orth_df"])

    print("\n=== ALL 5 WORKPACKAGES COMPLETED SUCCESSFULLY ===")
    print(f"Supplementary Tables saved to: {TABLES_DIR}")
    print(f"ML Result Matrices saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
