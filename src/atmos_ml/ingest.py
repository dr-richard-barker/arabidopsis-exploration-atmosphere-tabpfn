"""
Multi-Omics Data Ingestion, Metadata Forensics, and Physical Covariate Harmonization
for the Arabidopsis Exploration Atmosphere TabPFN Study.
"""
import os
import re
import gzip
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import numpy as np
import pandas as pd
from scipy import io as spio

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
DATA_DIR = PROJECT_DIR / "data" / "omics_matrices"


def parse_geo_series_matrix(path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parse a GEO series_matrix.txt.gz file into sample metadata and expression DataFrame."""
    meta = {}
    data_lines = []
    in_table = False
    with gzip.open(path, "rt", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if line.startswith("!Sample_"):
                parts = line.split("\t")
                key = parts[0][1:]
                vals = [p.strip('"') for p in parts[1:]]
                if key in meta:
                    meta[key] = [a + "; " + b for a, b in zip(meta[key], vals)]
                else:
                    meta[key] = vals
            elif line.startswith("!series_matrix_table_begin"):
                in_table = True
            elif line.startswith("!series_matrix_table_end"):
                in_table = False
            elif in_table and line.strip():
                data_lines.append(line.split("\t"))
    meta_df = pd.DataFrame(meta)
    if data_lines and len(data_lines) > 1:
        cols = [c.strip('"') for c in data_lines[0]]
        rows = [[ cell.strip('"') for cell in r ] for r in data_lines[1:]]
        expr_df = pd.DataFrame(rows, columns=cols).set_index(cols[0])
        expr_df = expr_df.apply(pd.to_numeric, errors="coerce")
    else:
        expr_df = pd.DataFrame()
    return meta_df, expr_df


def load_ath1_annotation() -> pd.DataFrame:
    """
    Load the complete Affymetrix Arabidopsis ATH1 (GPL198) probeset-to-TAIR10 gene mapping
    from NASA GeneLab GLDS-136 normalized expression table.
    """
    glds_path = DATA_DIR / "osdr" / "GLDS-136_array_normalized_expression_probeset_GLmicroarray.csv"
    df = pd.read_csv(glds_path)
    annot_cols = [
        "ProbesetID", "TAIR", "SYMBOL", "GENENAME", "REFSEQ",
        "ENTREZID", "STRING_id", "GOSLIM_IDS", "count_ENSEMBL_mappings"
    ]
    annot = df[annot_cols].copy()
    annot["ProbesetID"] = annot["ProbesetID"].astype(str)
    # Clean primary gene symbol (first symbol before pipe if multiple aliases)
    annot["PRIMARY_SYMBOL"] = (
        annot["SYMBOL"]
        .fillna(annot["TAIR"])
        .fillna(annot["ProbesetID"])
        .astype(str)
        .apply(lambda s: str(s).split("|")[0].strip() if pd.notna(s) and str(s) != "nan" else "")
    )
    annot.loc[annot["PRIMARY_SYMBOL"] == "", "PRIMARY_SYMBOL"] = annot["ProbesetID"].astype(str)
    annot = annot.set_index("ProbesetID")
    return annot


def _extract_cel_forensics(cel_filename: str) -> Dict[str, str]:
    """
    Extract hybridization batch ID, raw sample token, inferred organ, and inferred replicate letter
    from the raw Affymetrix CEL filename deposited in GEO/GeneLab.
    """
    base = os.path.basename(cel_filename).replace(".CEL.gz", "").replace(".cel.gz", "")
    # Remove GSM prefix if present
    parts = base.split("_")
    gsm = parts[0] if parts and parts[0].startswith("GSM") else ""
    batch_id = parts[1] if len(parts) > 1 and parts[1].isdigit() else "unknown"
    lower = base.lower()
    if "shoot" in lower or "_sh" in lower or "-sh" in lower:
        cel_organ = "Shoot"
    elif "root" in lower or "_rt" in lower or "-rt" in lower or "art" in lower:
        cel_organ = "Root"
    else:
        cel_organ = "Unknown"

    # Infer biological replicate letter (A, B, C) from CEL filename
    rep_letter = "Unknown"
    if re.search(r"(?:_|-|101|75|50|25|10|5|ox1|ox2|ox3|oxi)(a)(?:shoot|root|rt|_|-|\b)", lower):
        rep_letter = "A"
    elif re.search(r"(?:_|-|101|75|50|25|10|5|ox1|ox2|ox3|oxi)(b)(?:shoot|root|rt|_|-|\b)", lower):
        rep_letter = "B"
    elif re.search(r"(?:_|-|101|75|50|25|10|5|ox1|ox2|ox3|oxi)(c)(?:shoot|root|rt|_|-|\b)", lower):
        rep_letter = "C"
    elif "treatment_ox1_sh" in lower:
        rep_letter = "A_tech2"
    return {
        "cel_basename": base,
        "cel_batch_id": batch_id,
        "cel_organ": cel_organ,
        "cel_rep_letter": rep_letter,
    }


def _parse_hypobaric_sample_metadata(row: pd.Series, gse_id: str) -> Dict:
    """Parse physical and biological metadata from a GEO sample row in GSE87867/87868/87903/87904."""
    gsm = row["Sample_geo_accession"]
    title = str(row.get("Sample_title", ""))
    char = str(row.get("Sample_characteristics_ch1", ""))
    sup = str(row.get("Sample_supplementary_file", ""))
    cel_info = _extract_cel_forensics(sup)

    # Organ from title vs characteristics vs CEL
    title_organ = "Shoot" if "shoot" in title.lower() else ("Root" if "root" in title.lower() else "Unknown")
    if "tissue: shoots" in char.lower():
        char_organ = "Shoot"
    elif "tissue: roots" in char.lower():
        char_organ = "Root"
    else:
        char_organ = "Unknown"

    metadata_conflict_organ = (title_organ != char_organ) and (title_organ != "Unknown") and (char_organ != "Unknown")

    # Age (days)
    age_match = re.search(r"age:\s*(\d+)\s*day", char.lower())
    age_days = int(age_match.group(1)) if age_match else (5 if gse_id == "GSE87868" else 10)

    # Duration (hours)
    dur_match = re.search(r"for\s*(\d+)\s*hr", title.lower() + " " + char.lower())
    duration_h = int(dur_match.group(1)) if dur_match else 24

    # Pressure and O2 from title (authoritative over copy-paste errors in characteristics_ch1)
    t_low = title.lower()
    c_low = char.lower()
    if "control" in t_low or "97 kpa" in t_low:
        if "reduced oxygen" in t_low or "5.1 kpa" in t_low:
            p_total = 97.0
            p_o2 = 5.1
            regime = "Normobaric_Hypoxia_97kPa_5.1kPaO2"
            o2_supplemented = False
        else:
            p_total = 97.0
            p_o2 = 97.0 * 0.21  # 20.37 kPa
            regime = "Control_97kPa_Normoxia"
            o2_supplemented = False
    elif "75 kpa" in t_low:
        p_total = 75.0
        p_o2 = 75.0 * 0.21  # 15.75 kPa
        regime = "Hypobaria_75kPa_Air"
        o2_supplemented = False
    elif "50 kpa" in t_low:
        p_total = 50.0
        if "supplemented with oxygen" in t_low or "21 kpa" in t_low:
            p_o2 = 21.0
            regime = "Hypobaria_50kPa_NormoxicO2"
            o2_supplemented = True
        else:
            p_o2 = 50.0 * 0.21  # 10.50 kPa
            regime = "Hypobaria_50kPa_Air"
            o2_supplemented = False
    elif "25 kpa" in t_low:
        p_total = 25.0
        if "supplemented with oxygen" in t_low or "21 kpa" in t_low:
            p_o2 = 21.0
            regime = "Hypobaria_25kPa_NormoxicO2"
            o2_supplemented = True
        else:
            p_o2 = 25.0 * 0.21  # 5.25 kPa
            regime = "Hypobaria_25kPa_Air"
            o2_supplemented = False
    elif "10 kpa" in t_low:
        p_total = 10.0
        p_o2 = 10.0 * 0.21  # 2.10 kPa
        regime = "Hypobaria_10kPa_Air"
        o2_supplemented = False
    elif "5 kpa" in t_low:
        p_total = 5.0
        p_o2 = 5.0 * 0.21  # 1.05 kPa
        regime = "Hypobaria_5kPa_Air"
        o2_supplemented = False
    else:
        p_total = np.nan
        p_o2 = np.nan
        regime = "Unknown"
        o2_supplemented = False

    # Check if characteristics_ch1 had a pressure copy-paste conflict (e.g., GSM2342804, GSM2342805)
    char_p_match = re.search(r"exposed to:\s*(\d+)\s*kpa", c_low)
    char_p = float(char_p_match.group(1)) if char_p_match else p_total
    metadata_conflict_pressure = (abs(char_p - p_total) > 0.1)

    o2_frac = p_o2 / p_total if p_total > 0 else np.nan
    diffusivity_factor = 97.0 / p_total if p_total > 0 else np.nan
    hypobaria_index = np.log2(97.0 / p_total) if p_total > 0 else np.nan
    hypoxia_index = np.log2(20.37 / p_o2) if p_o2 > 0 else np.nan

    rep_match = re.search(r"(?:replica|rep)\s*(\d+)", t_low)
    rep_num = int(rep_match.group(1)) if rep_match else 1

    return {
        "gsm_id": gsm,
        "series_id": gse_id,
        "sample_title": title,
        "title_organ": title_organ,
        "char_organ": char_organ,
        "cel_organ": cel_info["cel_organ"],
        "consensus_organ": title_organ if title_organ != "Unknown" else char_organ,
        "metadata_conflict_organ": metadata_conflict_organ,
        "metadata_conflict_pressure": metadata_conflict_pressure,
        "age_days": age_days,
        "duration_h": duration_h,
        "P_total_kPa": p_total,
        "pO2_kPa": round(p_o2, 3),
        "O2_frac": round(o2_frac, 4),
        "o2_supplemented": o2_supplemented,
        "diffusivity_factor": round(diffusivity_factor, 4),
        "hypobaria_index": round(hypobaria_index, 4),
        "hypoxia_index": round(hypoxia_index, 4),
        "regime": regime,
        "rep_num": rep_num,
        "cel_basename": cel_info["cel_basename"],
        "cel_batch_id": cel_info["cel_batch_id"],
        "cel_rep_letter": cel_info["cel_rep_letter"],
    }


def load_core_hypobaric_arrays() -> Dict[str, pd.DataFrame]:
    """
    Load and harmonize all 4 core hypobaric series (GSE87867, GSE87868/GLDS-136, GSE87903, GSE87904).
    Returns a dictionary containing:
      - 'meta_all_entries': Metadata across all 148 series-level entries (including 18 shared GSMs)
      - 'meta_unique': Deduplicated metadata for the 130 unique GSMs
      - 'expr_rma_67_68_03': Exact RMA log2 expression matrix (22,746 probesets x 58 unique GSMs across GSE87867, GSE87868/GLDS-136, GSE87903)
      - 'expr_log2_all130': Harmonized log2 expression matrix across all 130 unique GSMs (22,746 probesets x 130 GSMs)
      - 'delta_log2_all130': Control-anchored response matrix (log2 sample - mean log2 matched 97 kPa control) across all 130 unique GSMs
      - 'shared_gsm_comparison': Verification table comparing the 18 shared GSMs between GSE87867 and GSE87903
      - 'annotation': ATH1 probeset-to-TAIR10 gene annotation table (22,746 biological probesets)
    """
    annot_full = load_ath1_annotation()

    # Load GSE87867 (33 samples, RMA log2)
    m67, e67 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE87867_series_matrix.txt.gz")
    # Load GSE87903 (34 samples, RMA log2)
    m03, e03 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE87903_series_matrix.txt.gz")
    # Load GSE87868 (9 samples, MAS5 in GEO; RMA log2 in GLDS-136)
    m68, e68_mas5 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE87868_series_matrix.txt.gz")
    glds136 = pd.read_csv(DATA_DIR / "osdr" / "GLDS-136_array_normalized_expression_probeset_GLmicroarray.csv")
    glds136 = glds136.set_index("ProbesetID")
    glds_sample_cols = [
        "Atha_Ws-0_root_97kPa_CTRL_Rep1", "Atha_Ws-0_root_97kPa_CTRL_Rep2", "Atha_Ws-0_root_97kPa_CTRL_Rep3",
        "Atha_Ws-0_root_50kPa_notsuppO2_Rep1", "Atha_Ws-0_root_50kPa_notsuppO2_Rep2", "Atha_Ws-0_root_50kPa_notsuppO2_Rep3",
        "Atha_Ws-0_root_50kPa_suppO2_Rep1", "Atha_Ws-0_root_50kPa_suppO2_Rep2", "Atha_Ws-0_root_50kPa_suppO2_Rep3",
    ]
    gsm68_ids = [f"GSM234210{i}" for i in range(9)]
    e68_rma = glds136[glds_sample_cols].copy()
    e68_rma.columns = gsm68_ids

    # Load GSE87904 (72 samples, MAS5 linear in GEO)
    m04, e04_mas5 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE87904_series_matrix.txt.gz")

    # Common biological probesets (22,746 non-AFFX control probesets)
    common_probes = e67.index.intersection(e03.index).intersection(e68_rma.index).intersection(e04_mas5.index)
    common_probes = [p for p in common_probes if not str(p).startswith("AFFX")]
    annot = annot_full.loc[common_probes].copy()

    e67 = e67.loc[common_probes]
    e03 = e03.loc[common_probes]
    e68_rma = e68_rma.loc[common_probes]
    e68_mas5 = e68_mas5.loc[common_probes]
    e04_mas5 = e04_mas5.loc[common_probes]

    # Compare the 18 shared GSMs between GSE87867 and GSE87903
    shared_gsms = sorted(list(set(e67.columns).intersection(set(e03.columns))))
    shared_rows = []
    for gsm in shared_gsms:
        v67 = e67[gsm].values
        v03 = e03[gsm].values
        diff = v67 - v03
        r = np.corrcoef(v67, v03)[0, 1]
        shared_rows.append({
            "gsm_id": gsm,
            "pearson_r": float(r),
            "max_abs_diff": float(np.max(np.abs(diff))),
            "rmse_diff": float(np.sqrt(np.mean(diff ** 2))),
            "mean_bias_67_minus_03": float(np.mean(diff)),
        })
    shared_comp_df = pd.DataFrame(shared_rows)

    # Parse metadata across all 4 series
    meta_records = []
    for gse_id, m_df in [("GSE87867", m67), ("GSE87868", m68), ("GSE87903", m03), ("GSE87904", m04)]:
        for _, r in m_df.iterrows():
            meta_records.append(_parse_hypobaric_sample_metadata(r, gse_id))
    meta_all = pd.DataFrame(meta_records)

    # Deduplicate to 130 unique GSMs (prioritizing GSE87867 entry for shared 18 GSMs, noting both series)
    shared_set = set(shared_gsms)
    meta_all["is_shared_67_03"] = meta_all["gsm_id"].isin(shared_set)
    meta_unique = meta_all.drop_duplicates(subset=["gsm_id"], keep="first").copy().set_index("gsm_id")
    meta_unique.loc[shared_gsms, "series_membership"] = "GSE87867;GSE87903"
    for gsm in meta_unique.index:
        if gsm not in shared_set:
            meta_unique.loc[gsm, "series_membership"] = meta_unique.loc[gsm, "series_id"]

    # Build RMA expression matrix for the 58 unique samples across GSE87867 (33), GSE87868 (9), and GSE87903_unique (16)
    e03_unique_cols = [c for c in e03.columns if c not in shared_set]
    expr_rma_58 = pd.concat([e67, e68_rma, e03[e03_unique_cols]], axis=1)

    # Convert GSE87904 MAS5 linear to log2 scale, and align quantiles to the reference RMA distribution
    # Note: For ML cross-validation, raw log2(MAS5) is also stored so fold-specific quantile alignment can be fit strictly on training folds.
    e04_log2_raw = np.log2(np.clip(e04_mas5, a_min=1.0, a_max=None))

    expr_log2_all130 = pd.concat([expr_rma_58, e04_log2_raw], axis=1)
    expr_log2_all130 = expr_log2_all130[meta_unique.index]

    # Compute within-study, organ/age/duration-matched control-anchored Delta log2FC
    # Each sample is anchored to the mean of its matched 97 kPa control group in the same series, organ, age, and duration
    delta_log2 = pd.DataFrame(index=expr_log2_all130.index, columns=expr_log2_all130.columns, dtype=float)

    # Wait: for GSE87903 unique samples (age_days labeled 11 in GEO for 75/10/5 kPa), their matched 97 kPa controls in GSE87903
    # are the 18 shared GSMs (GSM2342067-69 Root 97 kPa and GSM2342082-84 Shoot 97 kPa)!
    # Importantly, because GSE87903 was RMA-normalized as a 34-array batch, GSE87903 unique arrays should be anchored against
    # the GSE87903 RMA values of GSM2342067-69 (Root) and GSM2342082-84 (Shoot)!
    ctrl_67_root = e67[["GSM2342067", "GSM2342068", "GSM2342069"]].mean(axis=1)
    ctrl_67_shoot = e67[["GSM2342082", "GSM2342083", "GSM2342084"]].mean(axis=1)
    ctrl_03_root = e03[["GSM2342067", "GSM2342068", "GSM2342069"]].mean(axis=1)
    ctrl_03_shoot = e03[["GSM2342082", "GSM2342083", "GSM2342084"]].mean(axis=1)
    ctrl_68_root = e68_rma[["GSM2342100", "GSM2342101", "GSM2342102"]].mean(axis=1)

    for gsm, row in meta_unique.iterrows():
        s_id = row["series_id"]
        # Use expression-inferred organ for GSM2342806-809 after forensic verification, or title_organ (which is Shoot)
        organ = row["title_organ"]
        dur = row["duration_h"]
        if s_id == "GSE87867":
            ref = ctrl_67_root if organ == "Root" else ctrl_67_shoot
            delta_log2[gsm] = e67[gsm] - ref
        elif s_id == "GSE87868":
            delta_log2[gsm] = e68_rma[gsm] - ctrl_68_root
        elif s_id == "GSE87903":
            ref = ctrl_03_root if organ == "Root" else ctrl_03_shoot
            delta_log2[gsm] = e03[gsm] - ref
        elif s_id == "GSE87904":
            # Find matched 97 kPa controls in GSE87904 with same organ and duration_h
            ctrl_mask = (
                (meta_unique["series_id"] == "GSE87904")
                & (meta_unique["title_organ"] == organ)
                & (meta_unique["duration_h"] == dur)
                & (meta_unique["P_total_kPa"] == 97.0)
            )
            ctrl_gsms = meta_unique.index[ctrl_mask].tolist()
            ref = e04_log2_raw[ctrl_gsms].mean(axis=1)
            delta_log2[gsm] = e04_log2_raw[gsm] - ref

    return {
        "meta_all_entries": meta_all,
        "meta_unique": meta_unique,
        "expr_67": e67,
        "expr_03": e03,
        "expr_68_rma": e68_rma,
        "expr_68_mas5": e68_mas5,
        "expr_04_log2": e04_log2_raw,
        "expr_rma_58": expr_rma_58,
        "expr_log2_all130": expr_log2_all130,
        "delta_log2_all130": delta_log2,
        "shared_gsm_comparison": shared_comp_df,
        "annotation": annot,
    }


def load_trap_cell_type_arrays() -> Dict[str, pd.DataFrame]:
    """
    Load the Mustroph et al. (2009) cell-type specific TRAP-seq and total RNA hypoxia datasets
    (GSE14493: 20 arrays; GSE14502: 79 arrays, total = 99 arrays on GPL198 ATH1).
    """
    m493, e493 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE14493_series_matrix.txt.gz")
    m502, e502 = parse_geo_series_matrix(DATA_DIR / "geo_matrices" / "GSE14502_series_matrix.txt.gz")

    m493["series_id"] = "GSE14493"
    m502["series_id"] = "GSE14502"
    m_comb = pd.concat([m493, m502], ignore_index=True)

    # Map promoter lines to anatomical cell types/tissues per Mustroph et al. (2009) PNAS 106:18843-18848
    promoter_map = {
        "total": ("Whole-Organ Total RNA", "Whole Organ"),
        "p35s": ("Ubiquitous (35S)", "All tissues"),
        "prpl18": ("Ubiquitous (RPL18)", "All tissues"),
        "pscr": ("Endodermis / QC", "Root & Shoot Endodermis"),
        "pshr": ("Stele / Endodermis (SHR)", "Root Stele / Endodermis"),
        "pwol": ("Stele / Vasculature", "Root Stele / Pericycle"),
        "psultr2;2": ("Phloem Companion / Bundle Sheath", "Vasculature"),
        "psuc2": ("Phloem Companion Cells", "Phloem"),
        "papl": ("Phloem Sieve Elements / Companion", "Phloem"),
        "pathb8": ("Procambium / Protoxylem", "Vascular Cambium / Xylem"),
        "pcor": ("Cortex", "Root & Shoot Cortex"),
        "pco2": ("Meristematic Cortex", "Root Apical Cortex"),
        "ppep": ("Cortex (PEP)", "Root Cortex"),
        "pgl2": ("Atrichoblast Epidermis", "Root Non-Hair Epidermis / Trichomes"),
        "pcer5": ("Shoot Epidermis", "Leaf Cuticular Epidermis"),
        "pltp1": ("Epidermis (LTP1)", "Shoot & Root Tip Epidermis"),
        "prbcs": ("Photosynthetic Mesophyll", "Shoot Mesophyll / Guard Cells"),
        "ppet111": ("Columella Root Cap", "Root Cap"),
        "psuf4": ("Developing Vascular / Meristem", "Vascular / Meristem"),
    }

    records = []
    for _, r in m_comb.iterrows():
        gsm = r["Sample_geo_accession"]
        title = str(r.get("Sample_title", ""))
        char = str(r.get("Sample_characteristics_ch1", ""))
        tl = title.lower() + " " + char.lower()

        organ = "Root" if "root" in tl and "shoot" not in tl else ("Shoot" if "shoot" in tl and "root" not in tl else "Whole_Seedling")
        is_hypoxia = ("hypoxia" in tl or "hs" in title.lower() or "_h_" in title.lower() or "2h hypoxia" in tl) and ("control" not in tl and "normoxia" not in tl)
        has_sucrose = "sucrose" in tl or "hs_" in title.lower() or "ws_" in title.lower()
        rna_type = "Total_RNA" if "total" in title.lower() else "TRAP_Translatome"

        promo_found = "p35s"
        cell_type = "Ubiquitous (35S)"
        lineage_group = "All tissues"
        for pk, (ct, lg) in promoter_map.items():
            if pk in tl:
                promo_found = pk
                cell_type = ct
                lineage_group = lg
                break

        records.append({
            "gsm_id": gsm,
            "series_id": r["series_id"],
            "sample_title": title,
            "organ": organ,
            "promoter": promo_found,
            "cell_type": cell_type,
            "lineage_group": lineage_group,
            "is_hypoxia": is_hypoxia,
            "has_sucrose": has_sucrose,
            "rna_type": rna_type,
        })

    meta_trap = pd.DataFrame(records).set_index("gsm_id")
    expr_trap = pd.concat([e493, e502], axis=1)
    non_affx = [p for p in expr_trap.index if not str(p).startswith("AFFX")]
    expr_trap = expr_trap.loc[non_affx, meta_trap.index]
    return {"meta": meta_trap, "expr": expr_trap}


def load_zenodo_physiology_metabolomics() -> Dict[str, pd.DataFrame]:
    """
    Load all quantitative physiological and metabolomic workbooks from ZENODO16536514
    (62 kPa / 4000 m vs 101 kPa / 260 m factorial pressure x relative humidity study).
    """
    zdir = DATA_DIR / "zenodo_16536514"
    gas = pd.read_excel(zdir / "Gas_exchange_data.xlsx")
    gas = gas.rename(columns={"ai pressure (kPa)": "P_total_kPa", "HR": "RH_pct"})

    fluo = pd.read_excel(zdir / "Chlorophyll_fluorescence_parameters.xlsx")
    fluo = fluo.rename(columns={"air pressure (kPa)": "P_total_kPa"})

    nit = pd.read_excel(zdir / "Nitrogen_content_and_d13C.xlsx")
    nit = nit.rename(columns={"air pressure (kPa)": "P_total_kPa"})

    growth = pd.read_excel(zdir / "growth_measurements_arabidopsis.xlsx")
    growth = growth.rename(columns={"air pressure (kPa)": "P_total_kPa", "RH": "RH_pct", "numbver of plants": "n_plants"})

    pigments = pd.read_excel(zdir / "leaves_pigments.xlsx")
    pigments = pigments.rename(columns={"air pressure (kPa)": "P_total_kPa"})

    # Parse Metabolites_identification.xlsx cleanly
    met_raw = pd.read_excel(zdir / "Metabolites_identification.xlsx", header=1)
    sample_cols_row0 = met_raw.iloc[0]
    # Filter actual compound rows (where row index >= 1 and column 0 is numeric compound ID > 0)
    valid_mask = pd.to_numeric(met_raw.iloc[:, 0], errors="coerce") > 0
    met_df = met_raw.loc[valid_mask].copy()
    met_df = met_df.rename(columns={
        met_df.columns[0]: "compound_id",
        met_df.columns[1]: "mz_detected",
        met_df.columns[2]: "rt_min",
        met_df.columns[3]: "identification",
        met_df.columns[4]: "formula",
        met_df.columns[5]: "adduct",
        met_df.columns[9]: "metabolite_class",
        met_df.columns[10]: "opls_p1",
        met_df.columns[11]: "opls_p2",
        met_df.columns[15]: "p_value",
    })
    # Extract the 12 biological sample columns:
    # 260m_50% (cols 21, 22, 23), 4000m_50% (cols 24, 25, 26), 4000m_70% (cols 28, 29, 30), 260m_25% (cols 31, 32, 33)
    sample_map = {
        met_raw.columns[21]: "101kPa_RH50_Rep1",
        met_raw.columns[22]: "101kPa_RH50_Rep2",
        met_raw.columns[23]: "101kPa_RH50_Rep3",
        met_raw.columns[24]: "62kPa_RH50_Rep1",
        met_raw.columns[25]: "62kPa_RH50_Rep2",
        met_raw.columns[26]: "62kPa_RH50_Rep3",
        met_raw.columns[28]: "62kPa_RH70_Rep1",
        met_raw.columns[29]: "62kPa_RH70_Rep2",
        met_raw.columns[30]: "62kPa_RH70_Rep3",
        met_raw.columns[31]: "101kPa_RH25_Rep1",
        met_raw.columns[32]: "101kPa_RH25_Rep2",
        met_raw.columns[33]: "101kPa_RH25_Rep3",
    }
    met_df = met_df.rename(columns=sample_map)
    keep_cols = [
        "compound_id", "identification", "formula", "metabolite_class",
        "mz_detected", "rt_min", "opls_p1", "opls_p2", "p_value"
    ] + list(sample_map.values())
    met_df = met_df[keep_cols].copy()
    for c in list(sample_map.values()) + ["mz_detected", "rt_min", "opls_p1", "opls_p2", "p_value"]:
        met_df[c] = pd.to_numeric(met_df[c], errors="coerce")

    # Fill clean metabolite names and classes
    met_df["identification"] = met_df["identification"].fillna("Unidentified").astype(str).str.strip()
    met_df["metabolite_class"] = met_df["metabolite_class"].fillna("Unclassified").astype(str).str.strip()
    # Compute log2 fold changes across treatments relative to 101kPa_RH50
    ctrl_mean = met_df[["101kPa_RH50_Rep1", "101kPa_RH50_Rep2", "101kPa_RH50_Rep3"]].mean(axis=1)
    m62_50 = met_df[["62kPa_RH50_Rep1", "62kPa_RH50_Rep2", "62kPa_RH50_Rep3"]].mean(axis=1)
    m62_70 = met_df[["62kPa_RH70_Rep1", "62kPa_RH70_Rep2", "62kPa_RH70_Rep3"]].mean(axis=1)
    m101_25 = met_df[["101kPa_RH25_Rep1", "101kPa_RH25_Rep2", "101kPa_RH25_Rep3"]].mean(axis=1)

    met_df["log2FC_62kPa_RH50_vs_101kPa_RH50"] = np.log2((m62_50 + 1.0) / (ctrl_mean + 1.0))
    met_df["log2FC_62kPa_RH70_vs_101kPa_RH50"] = np.log2((m62_70 + 1.0) / (ctrl_mean + 1.0))
    met_df["log2FC_62kPa_RH70_vs_62kPa_RH50"] = np.log2((m62_70 + 1.0) / (m62_50 + 1.0))
    met_df["log2FC_101kPa_RH25_vs_101kPa_RH50"] = np.log2((m101_25 + 1.0) / (ctrl_mean + 1.0))

    return {
        "gas_exchange": gas,
        "fluorescence": fluo,
        "nitrogen_d13c": nit,
        "growth_rwc": growth,
        "pigments": pigments,
        "metabolites": met_df,
    }


def load_pxd002353_proteomics() -> pd.DataFrame:
    """
    Load and combine the 3 biological replicate batches of PXD002353 (Cho et al., J Exp Bot 2016)
    iTRAQ 8-plex quantitative proteomics across Col-0 and SnRK1.1K48M under 0, 0.5, 1, and 3 h submergence.
    Channels:
      113: Col-0 0h
      114/113: Col-0 0.5h / Col-0 0h
      115/113: Col-0 1h / Col-0 0h
      116/113: Col-0 3h / Col-0 0h
      117/113: SnRK1.1K48M 0h / Col-0 0h
      118/113: SnRK1.1K48M 0.5h / Col-0 0h
      119/113: SnRK1.1K48M 1h / Col-0 0h
      121/113: SnRK1.1K48M 3h / Col-0 0h
    """
    pdir = DATA_DIR / "proteomics"
    ratio_map = {
        "A6: 114/113": "Col0_0.5h_ratio",
        "A6: 115/113": "Col0_1h_ratio",
        "A6: 116/113": "Col0_3h_ratio",
        "A6: 117/113": "SnRK1K48M_0h_ratio",
        "A6: 118/113": "SnRK1K48M_0.5h_ratio",
        "A6: 119/113": "SnRK1K48M_1h_ratio",
        "A6: 121/113": "SnRK1K48M_3h_ratio",
    }
    batches = []
    for b_idx in [1, 2, 3]:
        df = pd.read_excel(pdir / f"PXD002353_batch{b_idx}.xlsx")
        df["TAIR"] = df["Accession"].astype(str).apply(lambda s: s.split(".")[0].strip().upper())
        df = df[df["TAIR"].str.match(r"^AT[1-5CM]G\d{5}$")].copy()
        df = df.rename(columns=ratio_map)
        keep = ["TAIR", "Description", "Σ# Unique Peptides", "Σ# PSMs"] + list(ratio_map.values())
        sub = df[keep].copy()
        sub["batch"] = b_idx
        for col in ratio_map.values():
            sub[col] = pd.to_numeric(sub[col], errors="coerce")
            sub[col.replace("_ratio", "_log2")] = np.log2(np.clip(sub[col], a_min=0.01, a_max=100.0))
        batches.append(sub)

    comb = pd.concat(batches, ignore_index=True)
    log2_cols = [c.replace("_ratio", "_log2") for c in ratio_map.values()]
    agg = comb.groupby("TAIR").agg(
        description=("Description", "first"),
        n_batches=("batch", "nunique"),
        mean_unique_peptides=("Σ# Unique Peptides", "mean"),
        mean_psms=("Σ# PSMs", "mean"),
        **{c: (c, "mean") for c in log2_cols},
        **{f"{c}_sd": (c, "std") for c in log2_cols},
    )
    # Compute SnRK1-dependent submergence response at 1h and 3h:
    # (SnRK1K48M_3h_log2 - SnRK1K48M_0h_log2) vs Col0_3h_log2
    agg["SnRK1K48M_submergence_3h_vs_0h_log2"] = agg["SnRK1K48M_3h_log2"] - agg["SnRK1K48M_0h_log2"]
    agg["SnRK1_dependency_3h_log2"] = agg["Col0_3h_log2"] - agg["SnRK1K48M_submergence_3h_vs_0h_log2"]
    return agg


def load_gse308672_snrnaseq() -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load the 4 single-nucleus RNA-seq MEX matrices for GSE308672 (5-day-old Col-0 root tips,
    4h normoxia 21% O2 vs 4h hypoxia 4% O2, 2 biological replicates each) if present.
    Assigns nuclei to major root cell lineages using canonical Shahan et al. (2022) / Brady et al. (2007)
    lineage marker genes and computes sample-level cell-lineage pseudobulk log2(CPM+1) profiles.
    """
    sndir = DATA_DIR / "snrnaseq_gse308672"
    samples = [
        ("GSM9251057", "GSM9251057_Wt.Normoxic.1", "Normoxia_21pct", 1),
        ("GSM9251058", "GSM9251058_Wt.Normoxic.2", "Normoxia_21pct", 2),
        ("GSM9251059", "GSM9251059_Wt.Hypoxic.1", "Hypoxia_4pct", 1),
        ("GSM9251060", "GSM9251060_Wt.Hypoxic.2", "Hypoxia_4pct", 2),
    ]
    for _, prefix, _, _ in samples:
        if not (sndir / f"{prefix}.matrix.mtx.gz").exists():
            return None

    # Canonical Arabidopsis root cell-type marker panels (Shahan et al. 2022 Dev Cell; Mustroph et al. 2009)
    lineage_markers = {
        "Stele_Pericycle": ["AT1G62990", "AT4G32880", "AT5G62940", "AT1G26770", "AT3G20840"],       # KNAT7, ATHB8, HCA2, EXP10, PLT1
        "Phloem": ["AT1G22710", "AT1G79430", "AT1G77210", "AT3G12750", "AT5G43610"],                # SUC2, APL, STP14, ZIF1, SUC6
        "Xylem": ["AT5G62380", "AT1G71930", "AT5G12870", "AT4G18780", "AT5G44030"],                 # VND6, VND7, MYB46, CESA8, CESA4
        "Endodermis": ["AT3G54220", "AT4G28720", "AT2G36100", "AT5G57620", "AT1G61590"],            # SCR, YUC8, CASP1, MYB36, SGN3
        "Cortex": ["AT1G09750", "AT1G62510", "AT3G03780", "AT5G03150", "AT2G47000"],                # PEP, EXT, MS2, JKD, ABCB4
        "Epidermis_Atrichoblast": ["AT1G79840", "AT5G53200", "AT2G37260", "AT1G65330", "AT5G14750"],# GL2, TRY, TTG2, PHE1, WER
        "Epidermis_Trichoblast": ["AT1G27740", "AT5G49270", "AT1G63650", "AT5G04960", "AT4G22080"], # RSL4, COBL9, EGL3, EXP7, RHS10
        "Columella_RootCap": ["AT1G79580", "AT3G10870", "AT4G27410", "AT1G26870", "AT5G20730"],     # SMB, MES17, RD26, FEZ, NPH4
        "Meristem_QC": ["AT3G11260", "AT2G03830", "AT1G51190", "AT3G20840", "AT5G10510"],           # WOX5, RGF8, PLT2, PLT1, AIL6
    }

    pseudobulk_records = []
    cell_summary_records = []
    gene_index = None
    pb_matrices = {}

    for gsm, prefix, cond, rep in samples:
        barcodes = pd.read_csv(sndir / f"{prefix}.barcodes.tsv.gz", sep="\t", header=None)[0].astype(str).tolist()
        genes_df = pd.read_csv(sndir / f"{prefix}.genes.tsv.gz", sep="\t", header=None)
        genes = genes_df[0].astype(str).apply(lambda s: s.split(".")[0].strip().upper()).tolist()
        with gzip.open(sndir / f"{prefix}.matrix.mtx.gz", "rb") as f:
            mat = spio.mmread(f).tocsr()  # shape: (n_genes, n_cells)

        if gene_index is None:
            gene_index = genes
        gene_to_idx = {g: i for i, g in enumerate(genes)}

        # Compute total UMIs per cell
        cell_totals = np.asarray(mat.sum(axis=0)).flatten()
        valid_cells = cell_totals >= 200
        mat_valid = mat[:, valid_cells]
        totals_valid = cell_totals[valid_cells]

        # Score each cell for each lineage using log1p(CPM) of lineage markers
        lineage_names = list(lineage_markers.keys())
        score_mat = np.zeros((len(lineage_names), mat_valid.shape[1]), dtype=np.float32)
        for l_idx, (lname, mgenes) in enumerate(lineage_markers.items()):
            valid_m = [gene_to_idx[g] for g in mgenes if g in gene_to_idx]
            if valid_m:
                sub_counts = np.asarray(mat_valid[valid_m, :].sum(axis=0)).flatten()
                score_mat[l_idx, :] = np.log2(1.0 + (sub_counts / np.maximum(totals_valid, 1.0)) * 1e4)

        best_lineage_idx = np.argmax(score_mat, axis=0)
        max_scores = np.max(score_mat, axis=0)

        # Sample-level whole-root pseudobulk log2(CPM + 1)
        sample_sum = np.asarray(mat_valid.sum(axis=1)).flatten()
        sample_cpm = (sample_sum / max(sample_sum.sum(), 1.0)) * 1e6
        pb_matrices[f"{gsm}_{cond}_Rep{rep}_WholeRoot"] = (
            pd.Series(np.log2(1.0 + sample_cpm), index=genes).groupby(level=0).mean()
        )

        # Lineage-specific pseudobulk log2(CPM + 1)
        for l_idx, lname in enumerate(lineage_names):
            mask = (best_lineage_idx == l_idx) & (max_scores > 0)
            n_cells = int(np.sum(mask))
            cell_summary_records.append({
                "gsm_id": gsm,
                "condition": cond,
                "rep": rep,
                "lineage": lname,
                "n_nuclei": n_cells,
                "pct_nuclei": 100.0 * n_cells / max(mat_valid.shape[1], 1),
                "total_valid_nuclei": int(mat_valid.shape[1]),
            })
            if n_cells >= 10:
                l_sum = np.asarray(mat_valid[:, mask].sum(axis=1)).flatten()
                l_cpm = (l_sum / max(l_sum.sum(), 1.0)) * 1e6
                pb_matrices[f"{gsm}_{cond}_Rep{rep}_{lname}"] = (
                    pd.Series(np.log2(1.0 + l_cpm), index=genes).groupby(level=0).mean()
                )

    pb_df = pd.DataFrame(pb_matrices).fillna(0.0)
    cell_summary_df = pd.DataFrame(cell_summary_records)
    return {
        "pseudobulk_log2cpm": pb_df,
        "cell_counts": cell_summary_df,
    }
