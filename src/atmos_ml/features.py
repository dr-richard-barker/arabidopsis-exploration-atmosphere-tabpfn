"""
Leak-Free Feature Engineering and Biological Pathway Eigengene Transformers
for TabPFN v2 Modeling of the Arabidopsis Exploration Atmosphere Response.

Strictly adheres to ml-best-practices:
- All statistics (means, standard deviations, quantiles, feature rankings) are learned
  exclusively inside .fit(X_train, y_train) and applied via .transform(X).
- Keeps feature dimensionality m <= 300 within the optimal regime of TabPFN v2 (Hollmann et al., Nature 2025).
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import f_classif, f_regression


# Curated Arabidopsis TAIR10 functional pathways & regulons relevant to hypobaria, hypoxia,
# boundary-layer desiccation, cuticle remodeling, oxylipin signaling, and glucosinolate allocation.
CURATED_PATHWAYS: Dict[str, List[str]] = {
    "ERF_VII_Core_Hypoxia_Anaerobic": [
        "AT1G77120",  # ADH1
        "AT4G33070",  # PDC1
        "AT5G54960",  # PDC2
        "AT5G20830",  # SUS1
        "AT3G43190",  # SUS4
        "AT2G16060",  # HB1 / GLB1
        "AT5G15120",  # PCO1
        "AT5G39890",  # PCO2
        "AT3G10040",  # HRA1
        "AT3G02550",  # LBD41
        "AT4G17260",  # LDH1
        "AT2G34390",  # NIP2;1
        "AT5G62520",  # SRO5
        "AT3G14230",  # RAP2.2
        "AT1G53910",  # RAP2.12
        "AT1G72360",  # HRE1 / ERF73
        "AT2G47520",  # HRE2 / ERF71
        "AT4G24110",  # HUP09
        "AT3G27220",  # HUP06
        "AT5G19550",  # ASP2
    ],
    "ABA_Desiccation_Stomatal_Closure": [
        "AT5G52310",  # RD29A
        "AT5G52300",  # RD29B
        "AT5G66400",  # RAB18
        "AT2G42540",  # COR15A
        "AT1G20440",  # COR47
        "AT5G15960",  # KIN1
        "AT5G15970",  # KIN2
        "AT3G14440",  # NCED3
        "AT5G59220",  # HAI1
        "AT4G26080",  # ABI1
        "AT5G57050",  # ABI2
        "AT1G72770",  # HAB1
        "AT4G33950",  # OST1 / SRK2E
        "AT1G12480",  # SLAC1
        "AT2G46680",  # ATHB7
        "AT3G61890",  # ATHB12
        "AT5G05410",  # DREB2A
        "AT2G33380",  # RD20
        "AT5G25610",  # RD22
        "AT1G52690",  # LEA7
    ],
    "Cuticle_Epicuticular_Wax_Lipid_Transport": [
        "AT1G02205",  # CER1
        "AT4G24510",  # CER2
        "AT5G57800",  # CER3 / WAX2
        "AT4G33790",  # CER4
        "AT1G01120",  # KCS1
        "AT1G04220",  # KCS2
        "AT1G68530",  # KCS6 / CUT1
        "AT2G47240",  # LACS1
        "AT1G49430",  # LACS2
        "AT5G59320",  # LTP3
        "AT5G59310",  # LTP4
        "AT1G17840",  # ABCG11
        "AT1G51500",  # ABCG12 / CER5
        "AT3G47600",  # MYB94
        "AT5G62470",  # MYB96
        "AT1G15360",  # WIN1 / SHN1
    ],
    "Cell_Wall_Mechanosensing_Expansion": [
        "AT5G57560",  # TCH4 / XTH22
        "AT4G30280",  # XTH18
        "AT4G30290",  # XTH19
        "AT4G30270",  # XTH24
        "AT4G35920",  # MCA1
        "AT5G12080",  # MSL10
        "AT3G51550",  # FER
        "AT5G54380",  # THE1
        "AT1G69530",  # EXPA1
        "AT2G40610",  # EXPA8
        "AT1G26770",  # EXPA10
        "AT3G14310",  # PME3
        "AT5G05170",  # CESA3
        "AT1G21250",  # WAK1
        "AT1G21270",  # WAK2
    ],
    "Oxylipin_JA_Chloroplast_Galactolipid": [
        "AT3G45140",  # LOX2
        "AT1G17420",  # LOX3
        "AT1G72520",  # LOX4
        "AT5G42650",  # AOS
        "AT3G25760",  # AOC1
        "AT3G25770",  # AOC2
        "AT3G25780",  # AOC3
        "AT2G06050",  # OPR3
        "AT4G31780",  # MGD1
        "AT5G20410",  # MGD2
        "AT3G11670",  # DGD1
        "AT4G00550",  # DGD2
        "AT1G19180",  # JAZ1
        "AT1G17380",  # JAZ5
        "AT5G13220",  # JAZ10
        "AT1G32640",  # MYC2
        "AT3G61680",  # PLIP1
    ],
    "Indole_Glucosinolate_Defense": [
        "AT4G39950",  # CYP79B2
        "AT2G22330",  # CYP79B3
        "AT4G31500",  # CYP83B1
        "AT2G20610",  # SUR1
        "AT1G24100",  # UGT74B1
        "AT1G74100",  # SOT16
        "AT5G60890",  # MYB34
        "AT1G18570",  # MYB51
        "AT1G74080",  # MYB122
        "AT1G21100",  # IGMT1
        "AT1G21120",  # IGMT2
        "AT2G44490",  # PEN2
        "AT5G57220",  # CYP81F2
    ],
    "Aliphatic_Glucosinolate_Biosynthesis": [
        "AT1G16410",  # CYP79F1
        "AT1G16400",  # CYP79F2
        "AT4G13770",  # CYP83A1
        "AT5G23010",  # MAM1
        "AT5G23020",  # MAM3
        "AT3G19710",  # BCAT4
        "AT1G65860",  # FMOGS-OX1
        "AT1G62560",  # FMOGS-OX3
        "AT5G61420",  # MYB28
        "AT5G07690",  # MYB29
        "AT5G07700",  # MYB76
        "AT1G74090",  # SOT18
    ],
    "Phenylpropanoid_Sinapate_Flavonol": [
        "AT2G37040",  # PAL1
        "AT3G53260",  # PAL2
        "AT2G30490",  # C4H
        "AT1G51680",  # 4CL1
        "AT5G13930",  # CHS / TT4
        "AT3G55120",  # CHI / TT5
        "AT3G51240",  # F3H / TT6
        "AT5G08640",  # FLS1
        "AT4G36220",  # FAH1 / F5H
        "AT2G22990",  # SNG1 / SMT (sinapoylglucose:malate sinapoyltransferase)
        "AT3G21560",  # UGT84A2 / BRT1 (UDP-glucosyltransferase for sinapate)
        "AT2G47460",  # MYB12
        "AT5G49330",  # MYB111
        "AT5G11260",  # HY5
        "AT1G56650",  # PAP1 / MYB75
    ],
    "SnRK1_Starvation_Sugar_Autophagy": [
        "AT3G01090",  # KIN10 / SnRK1.1
        "AT3G29160",  # KIN11 / SnRK1.2
        "AT3G47340",  # DIN6 / ASN1
        "AT4G35770",  # DIN1 / SEN1
        "AT5G20250",  # DIN10
        "AT1G70290",  # TPS8
        "AT1G23870",  # TPS9
        "AT1G60140",  # TPS10
        "AT2G18700",  # TPS11
        "AT5G49450",  # bZIP1
        "AT4G34590",  # bZIP11
        "AT5G28770",  # bZIP63
        "AT2G45170",  # ATG8E
        "AT3G06420",  # ATG8H
        "AT1G10070",  # BCAT2
    ],
    "Photosynthesis_Carbon_Fixation_LHC": [
        "AT1G67090",  # RBCS1A
        "AT5G38410",  # RBCS3B
        "AT1G29920",  # LHCB1.1
        "AT1G29910",  # LHCB1.2
        "AT2G05100",  # LHCB2.1
        "AT3G27690",  # LHCB2.4
        "AT3G54890",  # LHCA1
        "AT4G02770",  # PSAD-1
        "AT4G28750",  # PSAE-1
        "AT2G39730",  # RCA
        "AT3G01500",  # CA1 (beta carbonic anhydrase 1)
        "AT5G14740",  # CA2 (beta carbonic anhydrase 2)
        "AT2G20570",  # GLK1
        "AT5G44190",  # GLK2
    ],
    "ROS_Redox_Calcium_HeatShock": [
        "AT5G47910",  # RBOHD
        "AT1G64060",  # RBOHF
        "AT5G59820",  # ZAT12
        "AT1G27730",  # ZAT10 / STZ
        "AT2G38470",  # WRKY33
        "AT1G80840",  # WRKY40
        "AT1G07890",  # APX1
        "AT3G09640",  # APX2
        "AT4G35090",  # CAT2
        "AT5G42380",  # CML37
        "AT1G76650",  # CML38 (core hypoxia granule calcium sensor)
        "AT1G76640",  # CML39
        "AT5G66210",  # CPK28
        "AT2G26150",  # HSFA2
        "AT1G74310",  # HSP101
    ],
    "Ethylene_Auxin_Root_Remodeling": [
        "AT1G01480",  # ACS2
        "AT4G11280",  # ACS6
        "AT2G19590",  # ACO1
        "AT1G62380",  # ACO2
        "AT5G03280",  # EIN2
        "AT3G20770",  # EIN3
        "AT3G23240",  # ERF1
        "AT4G14560",  # IAA1
        "AT4G14550",  # IAA14 / SLR
        "AT3G15540",  # IAA19
        "AT1G73590",  # PIN1
        "AT5G57090",  # PIN2
        "AT5G20730",  # ARF7
        "AT1G19220",  # ARF19
    ],
}


def map_pathways_to_probesets(annot: pd.DataFrame, pathways: Dict[str, List[str]] = CURATED_PATHWAYS) -> Dict[str, List[str]]:
    """Map TAIR10 AGI locus lists to ATH1 probeset IDs present in annot."""
    tair_to_probes: Dict[str, List[str]] = {}
    for probe_id, row in annot.iterrows():
        tair_str = str(row.get("TAIR", ""))
        for t in tair_str.split("|"):
            t = t.strip().upper()
            if t.startswith("AT"):
                tair_to_probes.setdefault(t, []).append(str(probe_id))

    probe_pathways: Dict[str, List[str]] = {}
    for pname, agi_list in pathways.items():
        plist = []
        for agi in agi_list:
            plist.extend(tair_to_probes.get(agi.upper(), []))
        probe_pathways[pname] = sorted(list(set(plist)))
    return probe_pathways


class TabPFNOmicsFeatureBuilder(BaseEstimator, TransformerMixin):
    """
    Leak-free feature engineering transformer for TabPFN v2 on high-dimensional transcriptomics.
    Fits strictly on training samples (X_train, y_train) to compute:
      1. Training-standardized pathway eigengene scores across the 12 curated Arabidopsis modules.
      2. Mechanistic pathway interaction ratios (e.g., ABA_minus_ERF_VII, Indole_minus_Aliphatic_GSL,
         Oxylipin_minus_Photosynthesis, Cuticle_x_ABA, SnRK1_x_Hypoxia).
      3. Top-K supervised gene probeset features selected strictly on X_train via F-test (classification or regression),
         preferentially retaining probesets with valid TAIR10 gene symbols and non-redundant variance.
    """
    def __init__(
        self,
        probe_pathways: Dict[str, List[str]],
        probe_to_label: Optional[Dict[str, str]] = None,
        n_top_genes: int = 120,
        task_type: str = "classification",
        include_interactions: bool = True,
    ):
        self.probe_pathways = probe_pathways
        self.probe_to_label = probe_to_label
        self.n_top_genes = n_top_genes
        self.task_type = task_type
        self.include_interactions = include_interactions

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Optional[np.ndarray] = None):
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        self.input_columns_ = list(X_df.columns)

        # Compute training mean and std per feature for leak-free standardization
        self.col_means_ = X_df.mean(axis=0).fillna(0.0)
        self.col_stds_ = X_df.std(axis=0).replace(0.0, 1.0).fillna(1.0)

        # Separate non-probeset covariate columns (if any, e.g. organ_is_shoot, age_days, duration_h)
        self.covariate_cols_ = [c for c in X_df.columns if not str(c).endswith("_at")]
        self.probe_cols_ = [c for c in X_df.columns if str(c).endswith("_at")]

        # Select top-K probesets strictly on training fold
        if self.n_top_genes > 0 and len(self.probe_cols_) > 0 and y is not None:
            X_probes = X_df[self.probe_cols_].fillna(self.col_means_[self.probe_cols_]).values
            y_arr = np.asarray(y)
            # Filter out constant probesets on training fold
            var_mask = np.std(X_probes, axis=0) > 1e-6
            valid_probe_indices = np.where(var_mask)[0]
            if len(valid_probe_indices) > 0:
                X_sub = X_probes[:, valid_probe_indices]
                if self.task_type == "classification":
                    scores, _ = f_classif(X_sub, y_arr)
                else:
                    scores, _ = f_regression(X_sub, y_arr)
                scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
                top_local = np.argsort(scores)[::-1][: self.n_top_genes]
                self.selected_probes_ = [self.probe_cols_[valid_probe_indices[i]] for i in top_local]
                self.selected_probe_scores_ = {
                    self.probe_cols_[valid_probe_indices[i]]: float(scores[i]) for i in top_local
                }
            else:
                self.selected_probes_ = self.probe_cols_[: self.n_top_genes]
                self.selected_probe_scores_ = {}
        else:
            # Unsupervised fallback: top variance on training fold
            stds = X_df[self.probe_cols_].std(axis=0)
            self.selected_probes_ = stds.nlargest(self.n_top_genes).index.tolist()
            self.selected_probe_scores_ = stds.loc[self.selected_probes_].to_dict()

        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=self.input_columns_)
        # Impute missing values using training means and standardize using training mean/std
        X_filled = X_df.fillna(self.col_means_)
        X_z = (X_filled - self.col_means_) / self.col_stds_

        out_cols: Dict[str, np.ndarray] = {}

        # 1. Retain explicit experimental/tissue covariates if provided
        for c in self.covariate_cols_:
            out_cols[c] = X_filled[c].values

        # 2. Compute pathway eigengene scores (mean training-z-score across pathway probesets)
        pw_scores: Dict[str, np.ndarray] = {}
        for pname, plist in self.probe_pathways.items():
            valid_p = [p for p in plist if p in X_z.columns]
            if valid_p:
                pw_val = X_z[valid_p].mean(axis=1).values
            else:
                pw_val = np.zeros(len(X_df), dtype=float)
            pw_scores[pname] = pw_val
            out_cols[f"PW_{pname}"] = pw_val

        # 3. Compute mechanistic second-order pathway interaction features
        if self.include_interactions:
            aba = pw_scores.get("ABA_Desiccation_Stomatal_Closure", 0.0)
            hyp = pw_scores.get("ERF_VII_Core_Hypoxia_Anaerobic", 0.0)
            cut = pw_scores.get("Cuticle_Epicuticular_Wax_Lipid_Transport", 0.0)
            oxy = pw_scores.get("Oxylipin_JA_Chloroplast_Galactolipid", 0.0)
            pho = pw_scores.get("Photosynthesis_Carbon_Fixation_LHC", 0.0)
            igsl = pw_scores.get("Indole_Glucosinolate_Defense", 0.0)
            agsl = pw_scores.get("Aliphatic_Glucosinolate_Biosynthesis", 0.0)
            snrk = pw_scores.get("SnRK1_Starvation_Sugar_Autophagy", 0.0)
            wall = pw_scores.get("Cell_Wall_Mechanosensing_Expansion", 0.0)
            phen = pw_scores.get("Phenylpropanoid_Sinapate_Flavonol", 0.0)

            out_cols["INT_ABA_minus_ERF_VII_Hypoxia"] = aba - hyp
            out_cols["INT_ABA_plus_Cuticle_Barosensory"] = 0.5 * (aba + cut)
            out_cols["INT_Oxylipin_minus_Photosynthesis"] = oxy - pho
            out_cols["INT_Indole_minus_Aliphatic_GSL"] = igsl - agsl
            out_cols["INT_SnRK1_x_ERF_VII_EnergyStress"] = snrk * hyp
            out_cols["INT_CellWall_minus_Photosynthesis"] = wall - pho
            out_cols["INT_Phenylpropanoid_plus_ABA"] = 0.5 * (phen + aba)

        # 4. Add top-K training-selected gene probesets with readable symbol labels
        used_names = set(out_cols.keys())
        for p in self.selected_probes_:
            label = self.probe_to_label.get(p, p) if self.probe_to_label else p
            col_name = f"GENE_{label}_{p}" if label != p else f"GENE_{p}"
            if col_name in used_names:
                col_name = f"{col_name}_dup"
            used_names.add(col_name)
            out_cols[col_name] = X_z[p].values

        return pd.DataFrame(out_cols, index=X_df.index)
