"""
Mechanistic Interpretability, SHAP Attribution, and Orthogonal Axis Decomposition
for the Arabidopsis Exploration Atmosphere TabPFN v2 Study.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import shap


def compute_orthogonal_gene_decomposition(
    delta_log2: pd.DataFrame,
    meta_unique: pd.DataFrame,
    annot: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fit multivariable linear models across the 24-hour factorial hypobaric & oxygen-dissection arrays
    (GSE87867, GSE87868/OSD-136, GSE87903; n = 58 unique arrays) to decouple:
      - Pure Barosensory / Diffusivity effect: beta_hypobaria on log2(97 / P_total_kPa) controlling for pO2 and Organ
      - Pure Hypoxia / O2 partial pressure effect: beta_hypoxia on log2(20.37 / pO2_kPa) controlling for P_total and Organ
      - Organ-specific and developmental-stage (5d vs 10d Root) contrasts
      - Direct O2-supplementation persistence index at 50 kPa + O2 and 25 kPa + O2.
    """
    # Filter to the 58 24-h multi-pressure / O2-dissection arrays
    mask_58 = meta_unique["series_id"].isin(["GSE87867", "GSE87868", "GSE87903"])
    m58 = meta_unique.loc[mask_58].copy()
    Y = delta_log2[m58.index].values  # shape: (n_probes, 58)

    # Design matrix X: [Intercept, hypobaria_index, hypoxia_index, is_shoot]
    x_baro = m58["hypobaria_index"].values.astype(float)
    x_hypo = m58["hypoxia_index"].values.astype(float)
    x_shoot = (m58["consensus_organ"] == "Shoot").astype(float).values
    X = np.column_stack([np.ones(len(m58)), x_baro, x_hypo, x_shoot])

    # Vectorized OLS across all 22,746 probesets: B = (X^T X)^(-1) X^T Y^T
    XtX_inv = np.linalg.inv(X.T @ X)
    B = XtX_inv @ X.T @ Y.T  # shape: (4, n_probes)
    Y_hat = (X @ B).T        # shape: (n_probes, 58)
    residuals = Y - Y_hat
    dof = len(m58) - X.shape[1]
    mse = np.sum(residuals ** 2, axis=1) / dof  # shape: (n_probes,)

    se_baro = np.sqrt( np.maximum(mse * XtX_inv[1, 1], 1e-12) )
    se_hypo = np.sqrt( np.maximum(mse * XtX_inv[2, 2], 1e-12) )

    t_baro = B[1, :] / se_baro
    t_hypo = B[2, :] / se_hypo
    p_baro = 2.0 * stats.t.sf(np.abs(t_baro), df=dof)
    p_hypo = 2.0 * stats.t.sf(np.abs(t_hypo), df=dof)

    _, fdr_baro, _, _ = multipletests(p_baro, method="fdr_bh")
    _, fdr_hypo, _, _ = multipletests(p_hypo, method="fdr_bh")

    # Compute condition-specific mean Delta log2FCs
    def _cond_mean(regime_name: str, organ: Optional[str] = None, age: Optional[int] = None) -> np.ndarray:
        sub = m58["regime"] == regime_name
        if organ is not None:
            sub = sub & (m58["consensus_organ"] == organ)
        if age is not None:
            sub = sub & (m58["age_days"] == age)
        cols = m58.index[sub].tolist()
        if not cols:
            return np.zeros(delta_log2.shape[0])
        return delta_log2[cols].mean(axis=1).values

    d_75_air = _cond_mean("Hypobaria_75kPa_Air")
    d_50_air = _cond_mean("Hypobaria_50kPa_Air")
    d_50_o2 = _cond_mean("Hypobaria_50kPa_NormoxicO2")
    d_25_air = _cond_mean("Hypobaria_25kPa_Air")
    d_25_o2 = _cond_mean("Hypobaria_25kPa_NormoxicO2")
    d_97_hypo = _cond_mean("Normobaric_Hypoxia_97kPa_5.1kPaO2")
    d_10_air = _cond_mean("Hypobaria_10kPa_Air")
    d_5_air = _cond_mean("Hypobaria_5kPa_Air")

    # Organ & age specific contrasts at 50 kPa and 25 kPa
    d_50_air_root10 = _cond_mean("Hypobaria_50kPa_Air", organ="Root", age=10)
    d_50_o2_root10 = _cond_mean("Hypobaria_50kPa_NormoxicO2", organ="Root", age=10)
    d_50_air_root5 = _cond_mean("Hypobaria_50kPa_Air", organ="Root", age=5)
    d_50_o2_root5 = _cond_mean("Hypobaria_50kPa_NormoxicO2", organ="Root", age=5)
    d_50_air_shoot10 = _cond_mean("Hypobaria_50kPa_Air", organ="Shoot", age=10)
    d_50_o2_shoot10 = _cond_mean("Hypobaria_50kPa_NormoxicO2", organ="Shoot", age=10)
    d_25_air_shoot10 = _cond_mean("Hypobaria_25kPa_Air", organ="Shoot", age=10)
    d_25_o2_shoot10 = _cond_mean("Hypobaria_25kPa_NormoxicO2", organ="Shoot", age=10)

    # Pure barosensory response magnitude across O2-supplemented hypobaric regimes (50 kPa + O2 and 25 kPa + O2)
    pure_baro_effect = 0.5 * (d_50_o2 + d_25_o2)
    # Pure hypoxia response magnitude (97 kPa / 5.1 kPa O2 plus O2-reversible component at 25/50 kPa)
    pure_hypo_effect = 0.5 * (d_97_hypo + (d_25_air - d_25_o2))

    res = pd.DataFrame({
        "ProbesetID": delta_log2.index,
        "TAIR": annot.loc[delta_log2.index, "TAIR"].values,
        "SYMBOL": annot.loc[delta_log2.index, "PRIMARY_SYMBOL"].values,
        "GENENAME": annot.loc[delta_log2.index, "GENENAME"].values,
        "beta_hypobaria": B[1, :],
        "se_hypobaria": se_baro,
        "t_hypobaria": t_baro,
        "p_hypobaria": p_baro,
        "fdr_hypobaria": fdr_baro,
        "beta_hypoxia": B[2, :],
        "se_hypoxia": se_hypo,
        "t_hypoxia": t_hypo,
        "p_hypoxia": p_hypo,
        "fdr_hypoxia": fdr_hypo,
        "dlog2_75kPa_Air": d_75_air,
        "dlog2_50kPa_Air": d_50_air,
        "dlog2_50kPa_NormO2": d_50_o2,
        "dlog2_25kPa_Air": d_25_air,
        "dlog2_25kPa_NormO2": d_25_o2,
        "dlog2_97kPa_5.1kPaO2": d_97_hypo,
        "dlog2_10kPa_Air": d_10_air,
        "dlog2_5kPa_Air": d_5_air,
        "dlog2_50kPa_Air_Root10d": d_50_air_root10,
        "dlog2_50kPa_NormO2_Root10d": d_50_o2_root10,
        "dlog2_50kPa_Air_Root5d": d_50_air_root5,
        "dlog2_50kPa_NormO2_Root5d": d_50_o2_root5,
        "dlog2_50kPa_Air_Shoot10d": d_50_air_shoot10,
        "dlog2_50kPa_NormO2_Shoot10d": d_50_o2_shoot10,
        "dlog2_25kPa_Air_Shoot10d": d_25_air_shoot10,
        "dlog2_25kPa_NormO2_Shoot10d": d_25_o2_shoot10,
        "pure_barosensory_effect": pure_baro_effect,
        "pure_hypoxia_effect": pure_hypo_effect,
    }).set_index("ProbesetID")

    # Classify each responsive gene into mechanistic response axis
    axis_class = []
    for _, r in res.iterrows():
        b_abs = abs(r["beta_hypobaria"])
        h_abs = abs(r["beta_hypoxia"])
        baro_sig = (r["p_hypobaria"] < 0.01) or (abs(r["pure_barosensory_effect"]) >= 0.45)
        hypo_sig = (r["p_hypoxia"] < 0.01) or (abs(r["pure_hypoxia_effect"]) >= 0.60)
        if baro_sig and not hypo_sig:
            axis_class.append("Pure_Barosensory_Ptotal")
        elif hypo_sig and not baro_sig:
            axis_class.append("Pure_Hypoxia_pO2")
        elif baro_sig and hypo_sig:
            if b_abs > 1.35 * h_abs:
                axis_class.append("Predominantly_Barosensory")
            elif h_abs > 1.35 * b_abs:
                axis_class.append("Predominantly_Hypoxia")
            else:
                axis_class.append("Synergistic_Dual_Hub")
        else:
            axis_class.append("Background_Unchanged")
    res["mechanistic_axis"] = axis_class

    # Composite hub centrality score combining |t_hypobaria|, |t_hypoxia|, and |pure effects|
    res["hub_composite_score"] = (
        0.5 * np.abs(res["t_hypobaria"])
        + 0.5 * np.abs(res["t_hypoxia"])
        + np.abs(res["pure_barosensory_effect"])
        + np.abs(res["pure_hypoxia_effect"])
    )
    return res


def compute_tabpfn_shap_values(
    model,
    X_train: pd.DataFrame,
    X_eval: pd.DataFrame,
    n_coalitions: int = 8,
    random_state: int = 42,
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Compute batched antithetic Shapley permutation attributions for a trained TabPFN v2 model
    across all evaluation samples simultaneously (avoiding row-by-row unbatched Transformer calls).
    Satisfies Shapley efficiency and symmetry via paired forward/reverse antithetic coalitions.
    """
    rng = np.random.RandomState(random_state)
    X_tr = np.asarray(X_train, dtype=np.float32)
    X_ev = np.asarray(X_eval, dtype=np.float32)
    n_samples, n_features = X_ev.shape

    shap_vals = np.zeros((n_samples, n_features), dtype=np.float64)
    bg_indices = rng.choice(len(X_tr), size=n_coalitions, replace=True)

    # For each feature j, evaluate marginal contribution across antithetic random coalitions
    # batched across all n_samples simultaneously
    for j in range(n_features):
        batch_with_j = []
        batch_without_j = []
        for c_idx in range(n_coalitions):
            bg_row = X_tr[bg_indices[c_idx]]
            # Random subset mask S of other features (antithetic pair: mask and ~mask)
            mask = rng.rand(n_features) < 0.5
            if c_idx % 2 == 1:
                mask = ~prev_mask
            else:
                prev_mask = mask.copy()

            x_with = np.where(mask[None, :], X_ev, bg_row[None, :]).copy()
            x_without = x_with.copy()
            x_with[:, j] = X_ev[:, j]
            x_without[:, j] = bg_row[j]
            batch_with_j.append(x_with)
            batch_without_j.append(x_without)

        mat_with = np.vstack(batch_with_j)
        mat_without = np.vstack(batch_without_j)
        preds_both = model.predict(np.vstack([mat_with, mat_without]))
        half = len(mat_with)
        diffs = (preds_both[:half] - preds_both[half:]).reshape(n_coalitions, n_samples)
        shap_vals[:, j] = np.mean(diffs, axis=0)

    summary_df = pd.DataFrame({
        "feature": X_eval.columns,
        "mean_abs_shap": np.mean(np.abs(shap_vals), axis=0),
        "std_abs_shap": np.std(np.abs(shap_vals), axis=0),
        "mean_signed_shap": np.mean(shap_vals, axis=0),
    }).sort_values("mean_abs_shap", ascending=False)
    return shap_vals, summary_df

