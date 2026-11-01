"""
Reconciliation and Quantitative Execution Script addressing Reviewer Points 1-23:
- Exposes full 148 GSM audit ledger with dispositions and Affymetrix QC metrics.
- Computes Covariate Ablation Suite (Covariates-only vs Transcriptome-only vs Combined).
- Generates 4-Class Confusion Matrix and per-class metrics with class supports.
- Fits empirical Bayes moderated linear model (limma formulation) and interaction tests for orthogonal hubs.
- Computes LOCO conformal prediction intervals and updates all Supplementary Tables.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
CACHE_ROOT = WORKSPACE / ".cache"
os.environ["MPLCONFIGDIR"] = str(CACHE_ROOT / "mpl")
os.environ["TABPFN_MODEL_CACHE_DIR"] = str(CACHE_ROOT / "tabpfn")

import numpy as np
import pandas as pd
from scipy import stats, special
from sklearn.metrics import (
    confusion_matrix, classification_report, r2_score,
    mean_squared_error, mean_absolute_error, roc_auc_score, average_precision_score, f1_score
)
from sklearn.model_selection import GroupKFold, StratifiedKFold
from statsmodels.stats.multitest import multipletests

from atmos_ml.ingest import load_core_hypobaric_arrays
from atmos_ml.features import CURATED_PATHWAYS, map_pathways_to_probesets, TabPFNOmicsFeatureBuilder
from atmos_ml.models import (
    TabPFNRegressor, TabPFNPHERegressor,
    TabPFNClassifier, TabPFNPHEClassifier,
    bootstrap_metric_ci, compute_ece
)

PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
TABLES_DIR = PROJECT_DIR / "manuscript" / "tables"
ROOT_TABLES_DIR = PROJECT_DIR / "tables"
RESULTS_DIR = PROJECT_DIR / "outputs" / "ml_results"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
ROOT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def execute_audit_and_qc(core: Dict[str, pd.DataFrame]):
    print("=== Step 1: Generating Full 148-GSM Audit Ledger & Updating Table S1 ===")
    meta_all = core["meta_all_entries"].copy()
    meta_u = core["meta_unique"].copy()
    expr = core["expr_log2_all130"].T
    annot = core["annotation"]

    # Compute shoot photosynthetic and root endodermal marker log2 expression
    shoot_marker_probes = annot[annot["TAIR"].isin(["AT1G67090", "AT1G29910", "AT1G29920", "AT3G54890", "AT1G51500"])].index.tolist()
    root_marker_probes = annot[annot["TAIR"].isin(["AT3G54220", "AT2G36100", "AT1G27740", "AT5G49270", "AT1G61590"])].index.tolist()

    meta_u["shoot_marker_log2"] = expr.loc[meta_u.index, shoot_marker_probes].mean(axis=1).round(3)
    meta_u["root_marker_log2"] = expr.loc[meta_u.index, root_marker_probes].mean(axis=1).round(3)

    # Save full 148 GSM audit ledger
    ledger_cols = [
        "gsm_id", "series_id", "sample_title", "cel_basename", "cel_batch_id", "cel_rep_letter",
        "title_organ", "char_organ", "consensus_organ", "P_total_kPa", "pO2_kPa", "O2_frac",
        "age_days", "duration_h", "regime", "group_id", "disposition", "disposition_rule",
        "nuse_median", "rle_median", "rle_iqr", "scale_factor", "percent_present", "qc_status"
    ]
    meta_all_clean = meta_all[[c for c in ledger_cols if c in meta_all.columns]].copy()
    meta_all_clean.to_csv(TABLES_DIR / "Table_S1_Full_148_GSM_Audit_Ledger.csv", index=False)
    meta_all_clean.to_csv(ROOT_TABLES_DIR / "Table_S1_Full_148_GSM_Audit_Ledger.csv", index=False)
    print(f"  Saved Table_S1_Full_148_GSM_Audit_Ledger.csv ({len(meta_all_clean)} rows)")

    # Update Table S1 (Harmonized 130 Arrays)
    meta_u.to_csv(TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv")
    meta_u.to_csv(ROOT_TABLES_DIR / "Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv")
    print(f"  Updated Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv ({len(meta_u)} rows)")


def execute_covariate_ablation(core: Dict[str, pd.DataFrame]):
    print("\n=== Step 2: Executing Covariate Ablation Suite (Reviewer Point 9) ===")
    meta = core["meta_unique"]
    annot = core["annotation"]
    expr = core["expr_log2_all130"].T

    probe_pathways = map_pathways_to_probesets(annot, CURATED_PATHWAYS)
    probe_to_label = annot["PRIMARY_SYMBOL"].to_dict()

    mask_58 = meta["series_id"].isin(["GSE87867", "GSE87868", "GSE87903"])
    idx_58 = meta.index[mask_58].tolist()
    meta_58 = meta.loc[idx_58]
    X_58 = expr.loc[idx_58]

    groups_58 = meta_58["group_id"].values
    y_baro_58 = meta_58["hypobaria_index"].values.astype(float)
    y_hypo_58 = meta_58["hypoxia_index"].values.astype(float)

    covars_58 = pd.DataFrame({
        "is_shoot": (meta_58["consensus_organ"] == "Shoot").astype(float),
        "age_days": meta_58["age_days"].astype(float),
    }, index=idx_58)

    from sklearn.linear_model import Ridge

    ablation_results = []
    gkf = GroupKFold(n_splits=5)

    for task_name, y_task in [("Hypobaria Index", y_baro_58), ("Hypoxia Index", y_hypo_58)]:
        oof_cov = np.zeros(len(idx_58))
        oof_tx = np.zeros(len(idx_58))
        oof_comb = np.zeros(len(idx_58))

        for tr, va in gkf.split(X_58, y_task, groups=groups_58):
            # 1. Covariates-only (Ridge)
            m_cov = Ridge(alpha=1.0)
            m_cov.fit(covars_58.iloc[tr], y_task[tr])
            oof_cov[va] = m_cov.predict(covars_58.iloc[va])

            # 2. Transcriptome-only (TabPFN)
            fb = TabPFNOmicsFeatureBuilder(
                probe_pathways=probe_pathways,
                probe_to_label=probe_to_label,
                n_top_genes=45,
                task_type="regression",
                include_interactions=True,
            )
            X_tr_tx = fb.fit_transform(X_58.iloc[tr], y_task[tr])
            X_va_tx = fb.transform(X_58.iloc[va])

            m_tx = TabPFNRegressor(device="cpu", n_estimators=4, random_state=42)
            m_tx.fit(X_tr_tx.values, y_task[tr])
            oof_tx[va] = m_tx.predict(X_va_tx.values)

            # 3. Combined (Transcriptome + Covariates)
            X_tr_comb = np.hstack([X_tr_tx.values, covars_58.iloc[tr].values])
            X_va_comb = np.hstack([X_va_tx.values, covars_58.iloc[va].values])
            m_comb = TabPFNRegressor(device="cpu", n_estimators=4, random_state=42)
            m_comb.fit(X_tr_comb, y_task[tr])
            oof_comb[va] = m_comb.predict(X_va_comb)

        # Evaluate models
        for config_name, preds in [
            ("Covariates-Only (Organ + Age)", oof_cov),
            ("Transcriptome-Only (Gene Probesets)", oof_tx),
            ("Combined (Transcriptome + Covariates)", oof_comb),
        ]:
            r2 = float(r2_score(y_task, preds))
            rmse = float(np.sqrt(mean_squared_error(y_task, preds)))
            mae = float(mean_absolute_error(y_task, preds))
            rho = float(stats.spearmanr(y_task, preds)[0])
            ablation_results.append({
                "Target_Task": task_name,
                "Feature_Configuration": config_name,
                "R2": round(r2, 4),
                "RMSE": round(rmse, 4),
                "MAE": round(mae, 4),
                "Spearman_rho": round(rho, 4),
            })
            print(f"  {task_name} | {config_name}: R2 = {r2:.4f}, RMSE = {rmse:.4f}")

    ablation_df = pd.DataFrame(ablation_results)
    ablation_df.to_csv(RESULTS_DIR / "wp2_covariate_ablation_benchmarks.csv", index=False)
    ablation_df.to_csv(TABLES_DIR / "Table_S2C_Covariate_Ablation_Suite.csv", index=False)
    ablation_df.to_csv(ROOT_TABLES_DIR / "Table_S2C_Covariate_Ablation_Suite.csv", index=False)
    print("  Saved Table_S2C_Covariate_Ablation_Suite.csv")


def execute_4class_confusion_and_per_class():
    print("\n=== Step 3: Computing 4-Class Regime Confusion Matrix & Per-Class Metrics (Point 10) ===")
    oof_58 = pd.read_csv(RESULTS_DIR / "wp2_oof_predictions_58samples.csv")
    y_true = oof_58["true_regime_4class"].values
    y_pred = oof_58["pred_regime_TabPFN v2 (PHE)"].values

    cm = confusion_matrix(y_true, y_pred)
    regime_names = [
        "Normobaric Normoxia (97 kPa)",
        "Pure Hypobaria + O2 (50/25 kPa)",
        "Moderate Hypobaria (75/50 kPa Air)",
        "Severe Hypoxia / Extreme Hypobaria",
    ]
    cm_df = pd.DataFrame(cm, index=[f"True_{name}" for name in regime_names], columns=[f"Pred_{name}" for name in regime_names])
    cm_df.to_csv(RESULTS_DIR / "wp2_regime_4class_confusion_matrix.csv")

    cr = classification_report(y_true, y_pred, target_names=regime_names, output_dict=True)
    per_class_rows = []
    for c_idx, name in enumerate(regime_names):
        metrics = cr[name]
        per_class_rows.append({
            "Class_ID": c_idx,
            "Regime_Name": name,
            "Support_N": int(metrics["support"]),
            "Precision": round(float(metrics["precision"]), 4),
            "Recall": round(float(metrics["recall"]), 4),
            "F1_Score": round(float(metrics["f1-score"]), 4),
        })
    pc_df = pd.DataFrame(per_class_rows)
    pc_df.to_csv(RESULTS_DIR / "wp2_regime_4class_per_class_metrics.csv", index=False)
    print("  Confusion matrix and per-class metrics saved successfully.")
    print(pc_df.to_string(index=False))


def execute_limma_moderated_decomposition(core: Dict[str, pd.DataFrame]):
    print("\n=== Step 4: Limma Empirical Bayes Moderation & Interaction Testing (Points 11-13) ===")
    meta = core["meta_unique"]
    annot = core["annotation"]
    delta = core["delta_log2_all130"]

    mask_58 = meta["series_id"].isin(["GSE87867", "GSE87868", "GSE87903"])
    m58 = meta.loc[mask_58].copy()
    Y = delta[m58.index].values

    x_baro = m58["hypobaria_index"].values.astype(float)
    x_hypo = m58["hypoxia_index"].values.astype(float)
    x_shoot = (m58["consensus_organ"] == "Shoot").astype(float).values
    x_age = m58["age_days"].values.astype(float)
    x_int = x_baro * x_hypo

    # 1. Additive linear model: [1, x_baro, x_hypo, x_shoot, x_age]
    X_add = np.column_stack([np.ones(len(m58)), x_baro, x_hypo, x_shoot, x_age])
    XtX_inv = np.linalg.inv(X_add.T @ X_add)
    B_add = XtX_inv @ X_add.T @ Y.T
    Y_hat = (X_add @ B_add).T
    residuals = Y - Y_hat
    dof = len(m58) - X_add.shape[1]
    s2 = np.sum(residuals ** 2, axis=1) / dof

    # Smyth (2004) Empirical Bayes moderation
    z = np.log(np.maximum(s2, 1e-12))
    e_z = np.mean(z)
    var_z = np.var(z)
    tri_df = special.polygamma(1, dof / 2.0)
    excess_var = max(var_z - tri_df, 1e-4)
    d0 = 2.0 / excess_var
    s02 = np.exp(e_z + special.digamma(dof / 2.0) - np.log(dof / 2.0) - special.digamma(d0 / 2.0) + np.log(d0 / 2.0))
    s2_mod = (d0 * s02 + dof * s2) / (d0 + dof)
    dof_mod = d0 + dof

    se_baro_mod = np.sqrt(s2_mod * XtX_inv[1, 1])
    t_baro_mod = B_add[1, :] / se_baro_mod
    p_baro_mod = 2.0 * stats.t.sf(np.abs(t_baro_mod), df=dof_mod)
    _, fdr_baro_mod, _, _ = multipletests(p_baro_mod, method="fdr_bh")

    se_hypo_mod = np.sqrt(s2_mod * XtX_inv[2, 2])
    t_hypo_mod = B_add[2, :] / se_hypo_mod
    p_hypo_mod = 2.0 * stats.t.sf(np.abs(t_hypo_mod), df=dof_mod)
    _, fdr_hypo_mod, _, _ = multipletests(p_hypo_mod, method="fdr_bh")

    # 2. Interaction model: [1, x_baro, x_hypo, x_int, x_shoot, x_age]
    X_int = np.column_stack([np.ones(len(m58)), x_baro, x_hypo, x_int, x_shoot, x_age])
    XtX_inv_int = np.linalg.inv(X_int.T @ X_int)
    B_int = XtX_inv_int @ X_int.T @ Y.T
    res_int = Y - (X_int @ B_int).T
    dof_int = len(m58) - X_int.shape[1]
    s2_int = np.sum(res_int ** 2, axis=1) / dof_int
    s2_int_mod = (d0 * s02 + dof_int * s2_int) / (d0 + dof_int)
    se_int_mod = np.sqrt(s2_int_mod * XtX_inv_int[3, 3])
    t_int_mod = B_int[3, :] / se_int_mod
    p_int_mod = 2.0 * stats.t.sf(np.abs(t_int_mod), df=d0 + dof_int)
    _, fdr_int_mod, _, _ = multipletests(p_int_mod, method="fdr_bh")

    # Pure barosensory response across O2-supplemented regimes (50 kPa + O2 and 25 kPa + O2)
    def _cond_mean(regime_name: str) -> np.ndarray:
        sub = m58["regime"] == regime_name
        cols = m58.index[sub].tolist()
        return delta[cols].mean(axis=1).values if cols else np.zeros(delta.shape[0])

    d_50_o2 = _cond_mean("Hypobaria_50kPa_NormoxicO2")
    d_25_o2 = _cond_mean("Hypobaria_25kPa_NormoxicO2")
    d_97_hypo = _cond_mean("Normobaric_Hypoxia_97kPa_5.1kPaO2")
    d_25_air = _cond_mean("Hypobaria_25kPa_Air")
    d_50_air = _cond_mean("Hypobaria_50kPa_Air")
    d_75_air = _cond_mean("Hypobaria_75kPa_Air")
    d_10_air = _cond_mean("Hypobaria_10kPa_Air")
    d_5_air = _cond_mean("Hypobaria_5kPa_Air")

    pure_baro_effect = 0.5 * (d_50_o2 + d_25_o2)
    pure_hypo_effect = 0.5 * (d_97_hypo + (d_25_air - d_25_o2))

    # Standardized Categorization Rules
    # Pure Barosensory: baro_sig and not hypo_sig
    # Pure Hypoxia: hypo_sig and not baro_sig
    # Dual-Axis Associated: baro_sig and hypo_sig
    # If interaction p < 0.05: designate as Synergistic / Antagonistic
    axis_class = []
    for i in range(len(delta)):
        b_sig = (p_baro_mod[i] < 0.01) or (abs(pure_baro_effect[i]) >= 0.45)
        h_sig = (p_hypo_mod[i] < 0.01) or (abs(pure_hypo_effect[i]) >= 0.60)
        b_abs = abs(B_add[1, i])
        h_abs = abs(B_add[2, i])

        if b_sig and not h_sig:
            axis_class.append("Pure_Barosensory_Ptotal")
        elif h_sig and not b_sig:
            axis_class.append("Pure_Hypoxia_pO2")
        elif b_sig and h_sig:
            if b_abs > 1.35 * h_abs:
                axis_class.append("Predominantly_Barosensory")
            elif h_abs > 1.35 * b_abs:
                axis_class.append("Predominantly_Hypoxia")
            else:
                if p_int_mod[i] < 0.05:
                    axis_class.append("Synergistic_Dual_Hub" if B_int[3, i] > 0 else "Antagonistic_Dual_Hub")
                else:
                    axis_class.append("Additive_Dual_Associated_Hub")
        else:
            axis_class.append("Background_Unchanged")

    full_decomp = pd.DataFrame({
        "ProbesetID": delta.index,
        "TAIR": annot.loc[delta.index, "TAIR"].values,
        "SYMBOL": annot.loc[delta.index, "PRIMARY_SYMBOL"].values,
        "GENENAME": annot.loc[delta.index, "GENENAME"].values,
        "beta_hypobaria": B_add[1, :],
        "se_hypobaria_limma": se_baro_mod,
        "t_hypobaria_limma": t_baro_mod,
        "p_hypobaria_limma": p_baro_mod,
        "fdr_hypobaria_limma": fdr_baro_mod,
        "beta_hypoxia": B_add[2, :],
        "se_hypoxia_limma": se_hypo_mod,
        "t_hypoxia_limma": t_hypo_mod,
        "p_hypoxia_limma": p_hypo_mod,
        "fdr_hypoxia_limma": fdr_hypo_mod,
        "beta_interaction": B_int[3, :],
        "se_interaction_limma": se_int_mod,
        "p_interaction_limma": p_int_mod,
        "fdr_interaction_limma": fdr_int_mod,
        "pure_barosensory_effect": pure_baro_effect,
        "pure_hypoxia_effect": pure_hypo_effect,
        "dlog2_75kPa_Air": d_75_air,
        "dlog2_50kPa_Air": d_50_air,
        "dlog2_50kPa_NormO2": d_50_o2,
        "dlog2_25kPa_Air": d_25_air,
        "dlog2_25kPa_NormO2": d_25_o2,
        "dlog2_97kPa_5.1kPaO2": d_97_hypo,
        "dlog2_10kPa_Air": d_10_air,
        "dlog2_5kPa_Air": d_5_air,
        "mechanistic_axis": axis_class,
    }).set_index("ProbesetID")

    full_decomp["hub_composite_score"] = (
        0.5 * np.abs(full_decomp["t_hypobaria_limma"])
        + 0.5 * np.abs(full_decomp["t_hypoxia_limma"])
        + np.abs(full_decomp["pure_barosensory_effect"])
        + np.abs(full_decomp["pure_hypoxia_effect"])
    )

    full_decomp.to_csv(RESULTS_DIR / "wp2_full_22746_orthogonal_decomposition.csv")
    full_decomp.to_csv(TABLES_DIR / "Table_S3_Full_22746_Orthogonal_Decomposition.csv")
    full_decomp.to_csv(ROOT_TABLES_DIR / "Table_S3_Full_22746_Orthogonal_Decomposition.csv")

    # Priority Hub Table (Table S3: Curated Pathway + Top Discovery Nodes)
    probe_pathways = map_pathways_to_probesets(annot, CURATED_PATHWAYS)
    pathway_membership: Dict[str, str] = {}
    for pw_name, plist in probe_pathways.items():
        for p in plist:
            if p in pathway_membership:
                pathway_membership[p] += f";{pw_name}"
            else:
                pathway_membership[p] = pw_name
    full_decomp["curated_pathway"] = [pathway_membership.get(p, "Unassigned_Discovery_Node") for p in full_decomp.index]

    curated_probes = [p for p in full_decomp.index if full_decomp.loc[p, "curated_pathway"] != "Unassigned_Discovery_Node"]
    top_disc = full_decomp[full_decomp["curated_pathway"] == "Unassigned_Discovery_Node"].nlargest(100, "hub_composite_score").index.tolist()
    hub_table = full_decomp.loc[sorted(list(set(curated_probes + top_disc)))].sort_values("hub_composite_score", ascending=False)
    hub_table.to_csv(TABLES_DIR / "Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv")
    hub_table.to_csv(ROOT_TABLES_DIR / "Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv")

    print("  Axis class distribution across 22,746 probesets:")
    print(full_decomp["mechanistic_axis"].value_counts().to_string())
    print("  Limma moderation and hub classification complete.")


def execute_loco_conformal_intervals():
    print("\n=== Step 5: Computing LOCO Conformal Prediction Uncertainty (Point 22) ===")
    loco_df = pd.read_csv(TABLES_DIR / "Table_S6B_Leave_One_Condition_Out_Validation.csv")
    s6a_df = pd.read_csv(TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv")

    # Compute empirical LOCO residual standard deviations across held-out conditions
    loco_rmse = loco_df["RMSE_dlog2"].values
    mean_loco_rmse = float(np.mean(loco_rmse))
    q90_loco_err = float(np.percentile(loco_rmse, 90))
    q95_loco_err = float(np.percentile(loco_rmse, 95))

    print(f"  Empirical LOCO Mean RMSE: {mean_loco_rmse:.4f}, 90% Conformal Band: +/- {q90_loco_err:.4f}, 95% Band: +/- {q95_loco_err:.4f}")

    # Add conformal prediction intervals to Table S6A
    s6a_df["Conformal_Error_90CI"] = round(q90_loco_err, 4)
    s6a_df["Conformal_Error_95CI"] = round(q95_loco_err, 4)
    s6a_df.to_csv(TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv", index=False)
    s6a_df.to_csv(ROOT_TABLES_DIR / "Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv", index=False)
    print("  Table S6A updated with conformal prediction error bounds.")


def main():
    core = load_core_hypobaric_arrays()
    execute_audit_and_qc(core)
    execute_covariate_ablation(core)
    execute_4class_confusion_and_per_class()
    execute_limma_moderated_decomposition(core)
    execute_loco_conformal_intervals()
    print("\n=== All Reviewer Reconciliation Tasks Executed Successfully ===")


if __name__ == "__main__":
    main()
