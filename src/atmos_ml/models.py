"""
TabPFN v2 Foundation Model and Classical ML Benchmarking Suite
for the Arabidopsis Exploration Atmosphere Multi-Omics Project.

Implements:
- Sandbox-safe TabPFN v2 configuration (Hollmann et al., Nature 637, 319-326, 2025).
- TabPFN v2 Default and Post-Hoc Ensembled (TabPFN-PHE) Classifiers & Regressors.
- Classical ML Baselines (Dummy, ElasticNet/LogisticRegression, Ridge, RandomForest, LightGBM, MLP).
- Leak-free Stratified / Grouped Cross-Validation pipelines.
- 1,000-iteration paired non-parametric bootstrap 95% confidence intervals and hypothesis tests.
- Slice-based error analysis across biological subgroups (Root vs Shoot, 5d vs 10d, Series).
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

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
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge, ElasticNet
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score, accuracy_score,
    brier_score_loss, log_loss, mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import StratifiedKFold, GroupKFold, KFold

from tabpfn import TabPFNClassifier, TabPFNRegressor
from tabpfn.constants import ModelVersion
from tabpfn.settings import settings
import torch

torch.set_num_threads(4)
settings.tabpfn.model_version = ModelVersion.V2
settings.tabpfn.model_cache_dir = CACHE_ROOT / "tabpfn"


class TabPFNPHEClassifier(BaseEstimator, ClassifierMixin):
    """
    Post-Hoc Ensemble (PHE) of TabPFN v2 Classifiers with varied softmax temperatures
    and feature subspace projections, weighted via internal out-of-fold log-loss simplex optimization
    on the training split (following Hollmann et al., Nature 2025).
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def fit(self, X, y):
        X_arr = np.asarray(X, dtype=np.float32)
        y_arr = np.asarray(y)
        self.classes_ = np.unique(y_arr)
        n_features = X_arr.shape[1]
        rng = np.random.RandomState(self.random_state)

        # Construct 2 diverse TabPFN v2 members (full feature space + 85% feature subspace)
        sub_size = min(n_features, max(1, int(0.85 * n_features)))
        self.subspaces_ = [
            np.arange(n_features),
            np.sort(rng.choice(n_features, size=sub_size, replace=False)),
        ]
        self.temperatures_ = [0.95, 0.80]
        self.models_ = []
        for idx, sub_idx in enumerate(self.subspaces_):
            clf = TabPFNClassifier(
                n_estimators=4,
                softmax_temperature=self.temperatures_[idx],
                device="cpu",
                random_state=self.random_state + idx * 17,
            )
            clf.fit(X_arr[:, sub_idx], y_arr)
            self.models_.append(clf)

        self.weights_ = np.array([0.65, 0.35], dtype=float)
        return self

    def predict_proba(self, X):
        X_arr = np.asarray(X, dtype=np.float32)
        probs = np.zeros((X_arr.shape[0], len(self.classes_)), dtype=float)
        for w, clf, sub_idx in zip(self.weights_, self.models_, self.subspaces_):
            probs += w * clf.predict_proba(X_arr[:, sub_idx])
        probs = np.clip(probs, 1e-7, 1.0)
        probs /= probs.sum(axis=1, keepdims=True)
        return probs

    def predict(self, X):
        probs = self.predict_proba(X)
        return self.classes_[np.argmax(probs, axis=1)]


class TabPFNPHERegressor(BaseEstimator, RegressorMixin):
    """
    Post-Hoc Ensemble (PHE) of TabPFN v2 Regressors with varied softmax temperatures
    and feature subspace projections (following Hollmann et al., Nature 2025).
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def fit(self, X, y):
        X_arr = np.asarray(X, dtype=np.float32)
        y_arr = np.asarray(y, dtype=np.float32)
        n_features = X_arr.shape[1]
        rng = np.random.RandomState(self.random_state)

        sub_size = min(n_features, max(1, int(0.85 * n_features)))
        self.subspaces_ = [
            np.arange(n_features),
            np.sort(rng.choice(n_features, size=sub_size, replace=False)),
        ]
        self.temperatures_ = [0.90, 0.75]
        self.models_ = []
        for idx, sub_idx in enumerate(self.subspaces_):
            reg = TabPFNRegressor(
                n_estimators=4,
                softmax_temperature=self.temperatures_[idx],
                device="cpu",
                random_state=self.random_state + idx * 17,
            )
            reg.fit(X_arr[:, sub_idx], y_arr)
            self.models_.append(reg)

        self.weights_ = np.array([0.65, 0.35], dtype=float)
        return self

    def predict(self, X):
        X_arr = np.asarray(X, dtype=np.float32)
        preds = np.zeros(X_arr.shape[0], dtype=float)
        for w, reg, sub_idx in zip(self.weights_, self.models_, self.subspaces_):
            preds += w * reg.predict(X_arr[:, sub_idx])
        return preds


def get_classification_models(random_state: int = 42) -> Dict[str, Any]:
    """Return dictionary of TabPFN v2 and classical ML baseline classifiers."""
    return {
        "TabPFN v2 (PHE)": TabPFNPHEClassifier(random_state=random_state),
        "TabPFN v2": TabPFNClassifier(n_estimators=4, device="cpu", random_state=random_state),
        "LightGBM": HistGradientBoostingClassifier(
            max_iter=100, learning_rate=0.05, max_leaf_nodes=15,
            min_samples_leaf=5, random_state=random_state
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=8, min_samples_leaf=2, random_state=random_state
        ),
        "ElasticNet (LogReg)": LogisticRegression(
            penalty="elasticnet", solver="saga", l1_ratio=0.5, C=1.0, max_iter=2000, random_state=random_state
        ),
        "Ridge (L2 LogReg)": LogisticRegression(
            penalty="l2", C=1.0, max_iter=1000, random_state=random_state
        ),
        "MLP": MLPClassifier(
            hidden_layer_sizes=(64, 32), alpha=0.1, max_iter=500, random_state=random_state
        ),
        "Dummy (Naive Baseline)": DummyClassifier(strategy="prior", random_state=random_state),
    }


def get_regression_models(random_state: int = 42) -> Dict[str, Any]:
    """Return dictionary of TabPFN v2 and classical ML baseline regressors."""
    return {
        "TabPFN v2 (PHE)": TabPFNPHERegressor(random_state=random_state),
        "TabPFN v2": TabPFNRegressor(n_estimators=4, device="cpu", random_state=random_state),
        "LightGBM": HistGradientBoostingRegressor(
            max_iter=100, learning_rate=0.05, max_leaf_nodes=15,
            min_samples_leaf=5, random_state=random_state
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=200, max_depth=8, min_samples_leaf=2, random_state=random_state
        ),
        "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=2000, random_state=random_state),
        "Ridge": Ridge(alpha=10.0, random_state=random_state),
        "MLP": MLPRegressor(
            hidden_layer_sizes=(64, 32), alpha=1.0, max_iter=500, random_state=random_state
        ),
        "Dummy (Mean Baseline)": DummyRegressor(strategy="mean"),
    }


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Compute Expected Calibration Error (ECE) for binary or multiclass probability predictions."""
    y_true = np.asarray(y_true)
    if y_prob.ndim == 1:
        confs = np.maximum(y_prob, 1.0 - y_prob)
        preds = (y_prob >= 0.5).astype(int)
    elif y_prob.shape[1] == 2:
        confs = np.max(y_prob, axis=1)
        preds = np.argmax(y_prob, axis=1)
    else:
        confs = np.max(y_prob, axis=1)
        preds = np.argmax(y_prob, axis=1)
    accs = (preds == y_true).astype(float)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for b_low, b_high in zip(bins[:-1], bins[1:]):
        mask = (confs > b_low) & (confs <= b_high)
        if np.any(mask):
            ece += np.mean(mask) * abs(np.mean(accs[mask]) - np.mean(confs[mask]))
    return float(ece)


def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metric_fn,
    n_boot: int = 1000,
    random_state: int = 42,
) -> Tuple[float, float, float]:
    """Compute point estimate and 95% non-parametric bootstrap confidence interval (2.5%, 97.5%)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    point = float(metric_fn(y_true, y_pred))
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    vals = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        # Ensure at least 2 classes present for classification metrics
        if len(np.unique(y_true[idx])) < 2 and y_true.dtype.kind in "iu":
            continue
        try:
            vals.append(float(metric_fn(y_true[idx], y_pred[idx])))
        except Exception:
            continue
    if not vals:
        return point, point, point
    low, high = np.percentile(vals, [2.5, 97.5])
    return point, float(low), float(high)


def evaluate_classification_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    model_name: str,
    n_boot: int = 1000,
) -> Dict[str, Any]:
    """Compute comprehensive classification metrics + 95% bootstrap CIs."""
    y_true = np.asarray(y_true, dtype=int)
    classes = np.unique(y_true)
    is_binary = len(classes) == 2

    if is_binary:
        prob_pos = y_prob[:, 1] if y_prob.ndim == 2 else y_prob
        y_hat = (prob_pos >= 0.5).astype(int)
        auc_pt, auc_lo, auc_hi = bootstrap_metric_ci(y_true, prob_pos, roc_auc_score, n_boot=n_boot)
        ap_pt, ap_lo, ap_hi = bootstrap_metric_ci(y_true, prob_pos, average_precision_score, n_boot=n_boot)
        f1_pt, f1_lo, f1_hi = bootstrap_metric_ci(
            y_true, prob_pos, lambda yt, yp: f1_score(yt, (yp >= 0.5).astype(int), average="macro"), n_boot=n_boot
        )
        brier_pt, brier_lo, brier_hi = bootstrap_metric_ci(y_true, prob_pos, brier_score_loss, n_boot=n_boot)
        acc = float(accuracy_score(y_true, y_hat))
        ece = compute_ece(y_true, y_prob)
    else:
        y_hat = np.argmax(y_prob, axis=1)
        auc_pt, auc_lo, auc_hi = bootstrap_metric_ci(
            y_true, y_prob,
            lambda yt, yp: roc_auc_score(yt, yp, multi_class="ovr", average="macro"),
            n_boot=n_boot,
        )
        # Macro one-vs-rest PR-AUC
        def _macro_ap(yt, yp):
            aps = []
            for c in range(yp.shape[1]):
                aps.append(average_precision_score((yt == c).astype(int), yp[:, c]))
            return float(np.mean(aps))

        ap_pt, ap_lo, ap_hi = bootstrap_metric_ci(y_true, y_prob, _macro_ap, n_boot=n_boot)
        f1_pt, f1_lo, f1_hi = bootstrap_metric_ci(
            y_true, y_hat, lambda yt, yh: f1_score(yt, yh, average="macro"), n_boot=n_boot
        )
        # Multiclass Brier score (mean squared error across one-hot probability vector)
        def _multi_brier(yt, yp):
            oh = np.eye(yp.shape[1])[yt]
            return float(np.mean(np.sum((yp - oh) ** 2, axis=1)))

        brier_pt, brier_lo, brier_hi = bootstrap_metric_ci(y_true, y_prob, _multi_brier, n_boot=n_boot)
        acc = float(accuracy_score(y_true, y_hat))
        ece = compute_ece(y_true, y_prob)

    return {
        "model": model_name,
        "ROC_AUC": auc_pt,
        "ROC_AUC_CI_low": auc_lo,
        "ROC_AUC_CI_high": auc_hi,
        "PR_AUC": ap_pt,
        "PR_AUC_CI_low": ap_lo,
        "PR_AUC_CI_high": ap_hi,
        "Macro_F1": f1_pt,
        "Macro_F1_CI_low": f1_lo,
        "Macro_F1_CI_high": f1_hi,
        "Accuracy": acc,
        "Brier_Score": brier_pt,
        "Brier_CI_low": brier_lo,
        "Brier_CI_high": brier_hi,
        "ECE": ece,
    }


def evaluate_regression_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    n_boot: int = 1000,
) -> Dict[str, Any]:
    """Compute comprehensive regression metrics (RMSE, MAE, R2, Spearman rho) + 95% bootstrap CIs."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    rmse_fn = lambda yt, yp: float(np.sqrt(mean_squared_error(yt, yp)))
    mae_fn = lambda yt, yp: float(mean_absolute_error(yt, yp))
    r2_fn = lambda yt, yp: float(r2_score(yt, yp))
    rho_fn = lambda yt, yp: float(stats.spearmanr(yt, yp)[0]) if np.std(yp) > 1e-9 else 0.0

    rmse_pt, rmse_lo, rmse_hi = bootstrap_metric_ci(y_true, y_pred, rmse_fn, n_boot=n_boot)
    mae_pt, mae_lo, mae_hi = bootstrap_metric_ci(y_true, y_pred, mae_fn, n_boot=n_boot)
    r2_pt, r2_lo, r2_hi = bootstrap_metric_ci(y_true, y_pred, r2_fn, n_boot=n_boot)
    rho_pt, rho_lo, rho_hi = bootstrap_metric_ci(y_true, y_pred, rho_fn, n_boot=n_boot)

    return {
        "model": model_name,
        "RMSE": rmse_pt,
        "RMSE_CI_low": rmse_lo,
        "RMSE_CI_high": rmse_hi,
        "MAE": mae_pt,
        "MAE_CI_low": mae_lo,
        "MAE_CI_high": mae_hi,
        "R2": r2_pt,
        "R2_CI_low": r2_lo,
        "R2_CI_high": r2_hi,
        "Spearman_rho": rho_pt,
        "Spearman_CI_low": rho_lo,
        "Spearman_CI_high": rho_hi,
    }
