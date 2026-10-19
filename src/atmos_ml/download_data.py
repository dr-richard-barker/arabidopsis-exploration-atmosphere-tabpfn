"""Download public omics matrices, physiological workbooks, and TabPFN v2 model weights."""
from __future__ import annotations
import os
import sys
import json
import time
import hashlib
import urllib.parse
from pathlib import Path

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
CACHE_ROOT = WORKSPACE / ".cache"
for subdir in ["skrub", "hf", "torch", "mpl", "tabpfn"]:
    (CACHE_ROOT / subdir).mkdir(parents=True, exist_ok=True)

os.environ["SKRUB_DATA_DIRECTORY"] = str(CACHE_ROOT / "skrub")
os.environ["HF_HOME"] = str(CACHE_ROOT / "hf")
os.environ["TORCH_HOME"] = str(CACHE_ROOT / "torch")
os.environ["MPLCONFIGDIR"] = str(CACHE_ROOT / "mpl")
os.environ["TABPFN_MODEL_CACHE_DIR"] = str(CACHE_ROOT / "tabpfn")
os.environ["XDG_CACHE_HOME"] = str(CACHE_ROOT)

import numpy as np
import requests

DATA_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere" / "data" / "omics_matrices"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def warmup_tabpfn():
    print("=== Step 1: Warming up TabPFN v2 Classifier & Regressor checkpoints ===")
    from tabpfn import TabPFNClassifier, TabPFNRegressor
    from tabpfn.constants import ModelVersion
    from tabpfn.settings import settings

    settings.tabpfn.model_version = ModelVersion.V2
    settings.tabpfn.model_cache_dir = CACHE_ROOT / "tabpfn"

    rng = np.random.default_rng(42)
    X = rng.normal(size=(30, 6)).astype(np.float32)
    y_cls = np.array([0, 1] * 15)
    y_reg = X[:, 0] * 2.0 - X[:, 1] + rng.normal(scale=0.1, size=30).astype(np.float32)

    clf = TabPFNClassifier(device="cpu", n_estimators=2)
    clf.fit(X[:20], y_cls[:20])
    probs = clf.predict_proba(X[20:])
    print("TabPFNClassifier v2 warmup success, probs shape:", probs.shape)

    reg = TabPFNRegressor(device="cpu", n_estimators=2)
    reg.fit(X[:20], y_reg[:20])
    preds = reg.predict(X[20:])
    print("TabPFNRegressor v2 warmup success, preds shape:", preds.shape)


def download_file(url: str, dest: Path, max_mb: float = 250.0, headers: dict | None = None) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 100:
        h = hashlib.sha256(dest.read_bytes()).hexdigest()
        print(f"  [CACHED] {dest.name} ({dest.stat().st_size:,} bytes)")
        return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": "cached", "bytes": dest.stat().st_size, "sha256": h}

    req_headers = {"User-Agent": "ArabidopsisExplorationAtmosphereML/0.2.0 (Academic Research)"}
    if headers:
        req_headers.update(headers)

    try:
        with requests.get(url, headers=req_headers, stream=True, timeout=60) as r:
            if r.status_code != 200:
                print(f"  [WARN] HTTP {r.status_code} for {url}")
                return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": f"http_{r.status_code}", "bytes": 0}
            cl = r.headers.get("Content-Length")
            if cl and int(cl) > max_mb * 1024 * 1024:
                print(f"  [SKIP-LARGE] {dest.name} is {int(cl)/1e6:.1f} MB > {max_mb} MB limit")
                return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": "skipped_large", "bytes": int(cl)}
            hasher = hashlib.sha256()
            total = 0
            tmp = dest.with_suffix(dest.suffix + ".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
                        hasher.update(chunk)
                        total += len(chunk)
                        if total > max_mb * 1024 * 1024:
                            tmp.unlink(missing_ok=True)
                            print(f"  [ABORT-LARGE] {dest.name} exceeded {max_mb} MB")
                            return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": "aborted_large", "bytes": total}
            tmp.replace(dest)
            print(f"  [OK] {dest.name} ({total:,} bytes)")
            return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": "downloaded", "bytes": total, "sha256": hasher.hexdigest()}
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return {"url": url, "file": str(dest.relative_to(WORKSPACE)), "status": f"error: {e}", "bytes": 0}


def main():
    manifest_log = []
    warmup_tabpfn()

    print("\n=== Step 2: Downloading GEO Series Matrix Files & GPL198 Annotation ===")
    geo_series = [
        ("GSE87867", "GSE87nnn"),
        ("GSE87868", "GSE87nnn"),
        ("GSE87903", "GSE87nnn"),
        ("GSE87904", "GSE87nnn"),
        ("GSE14493", "GSE14nnn"),
        ("GSE14502", "GSE14nnn"),
        ("GSE11558", "GSE11nnn"),
        ("GSE308672", "GSE308nnn"),
    ]
    for gse, prefix in geo_series:
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse}/matrix/{gse}_series_matrix.txt.gz"
        dest = DATA_DIR / "geo_matrices" / f"{gse}_series_matrix.txt.gz"
        manifest_log.append(download_file(url, dest))

    # Also download raw tar archives for the core hypobaria studies in case CEL or supplemental files are needed
    for gse, prefix in [("GSE87867", "GSE87nnn"), ("GSE87868", "GSE87nnn"), ("GSE87903", "GSE87nnn")]:
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse}/suppl/{gse}_RAW.tar"
        dest = DATA_DIR / "geo_raw" / f"{gse}_RAW.tar"
        manifest_log.append(download_file(url, dest, max_mb=150.0))

    # GSE308672 single-nucleus root hypoxia MEX matrices (GSM9251057-GSM9251060)
    sn_samples = [
        ("GSM9251057", "GSM9251057_Wt.Normoxic.1"),
        ("GSM9251058", "GSM9251058_Wt.Normoxic.2"),
        ("GSM9251059", "GSM9251059_Wt.Hypoxic.1"),
        ("GSM9251060", "GSM9251060_Wt.Hypoxic.2"),
    ]
    for gsm, prefix in sn_samples:
        for suffix in ["barcodes.tsv.gz", "genes.tsv.gz", "matrix.mtx.gz"]:
            fname = f"{prefix}.{suffix}"
            url = f"https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM9251nnn/{gsm}/suppl/{fname}"
            dest = DATA_DIR / "snrnaseq_gse308672" / fname
            manifest_log.append(download_file(url, dest, max_mb=100.0))

    # GPL198 platform annotation (AGI TAIR10 locus mapping & gene symbols)
    gpl_urls = [
        ("https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPLnnn/GPL198/annot/GPL198.annot.gz", DATA_DIR / "annotations" / "GPL198.annot.gz"),
        ("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL198&targ=self&form=text&view=full", DATA_DIR / "annotations" / "GPL198_full.soft"),
    ]
    for url, dest in gpl_urls:
        manifest_log.append(download_file(url, dest, max_mb=100.0))

    print("\n=== Step 3: Downloading NASA OSDR / GeneLab Processed Files (OSD-136 & OSD-134) ===")
    osdr_files = [
        ("OSD-136", "GLDS-136_array_SampleTable_GLmicroarray.csv"),
        ("OSD-136", "GLDS-136_array_contrasts_GLmicroarray.csv"),
        ("OSD-136", "GLDS-136_array_differential_expression_GLmicroarray.csv"),
        ("OSD-136", "GLDS-136_array_normalized_expression_probeset_GLmicroarray.csv"),
        ("OSD-136", "GLDS-136_array_microarray_v0_runsheet.csv"),
        ("OSD-136", "OSD-136_metadata_GSE87868-ISA.zip"),
        ("OSD-134", "OSD-134_metadata_OSD-134-ISA.zip"),
    ]
    for osd, fname in osdr_files:
        url = f"https://osdr.nasa.gov/geode-py/ws/studies/{osd}/download?source=datamanager&file={fname}"
        dest = DATA_DIR / "osdr" / fname
        manifest_log.append(download_file(url, dest, max_mb=100.0))

    print("\n=== Step 4: Downloading Zenodo 16536514 Low-Pressure Physiology & Metabolomics Workbooks ===")
    zenodo_files = [
        "Chlorophyll fluorescence parameters.xlsx",
        "Ecotron_CO2_1_min_values.xlsx",
        "Gas exchange data.xlsx",
        "Metabolites identification.xlsx",
        "Nitrogen content and d13C.xlsx",
        "growth_measurements_arabidopsis.xlsx",
        "leaves pigments.xlsx",
    ]
    for fname in zenodo_files:
        encoded = urllib.parse.quote(fname)
        url = f"https://zenodo.org/records/16536514/files/{encoded}?download=1"
        dest = DATA_DIR / "zenodo_16536514" / fname.replace(" ", "_")
        res = download_file(url, dest, max_mb=50.0)
        if res["status"] != "downloaded" and res["status"] != "cached":
            # Fallback Zenodo API content endpoint
            url2 = f"https://zenodo.org/api/records/16536514/files/{encoded}/content"
            res = download_file(url2, dest, max_mb=50.0)
        manifest_log.append(res)

    print("\n=== Step 5: Downloading GSE308672 Root Hypoxia snRNA-seq & Proteomics / Ethylene Comparators ===")
    sn_url = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE308nnn/GSE308672/suppl/GSE308672_RAW.tar"
    manifest_log.append(download_file(sn_url, DATA_DIR / "snrnaseq_GSE308672" / "GSE308672_RAW.tar", max_mb=200.0))

    # Also check PMC12917472 BioC / full text for GSE308672 cell-type marker / DE tables
    pmc_url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC12917472/unicode"
    manifest_log.append(download_file(pmc_url, DATA_DIR / "snrnaseq_GSE308672" / "PMC12917472_bioc.json", max_mb=25.0))

    # Also fetch full text BioC JSON for the 2017 Ferl/Paul hypobaria papers & Apelt atlas to verify design & marker details
    extra_pmc = [
        ("PMC5385329_Zhou2017_fpls.json", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC5385329/unicode"),
        ("PMC5553264_Zhou2017_aobpla.json", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC5553264/unicode"),
        ("PMC8825464_Apelt2022_atlas.json", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC8825464/unicode"),
        ("PMC2690036_Mustroph2009_TRAP.json", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC2690036/unicode"),
    ]
    for name, url in extra_pmc:
        manifest_log.append(download_file(url, DATA_DIR / "literature_bioc" / name, max_mb=25.0))

    # Proteomics & ethylene-hypoxia comparators
    comp_urls = [
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2016/04/PXD002353/07152013A520SHIHbatch1.xlsx", DATA_DIR / "proteomics" / "PXD002353_batch1.xlsx"),
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2016/04/PXD002353/07152013A520SHIHbatch2.xlsx", DATA_DIR / "proteomics" / "PXD002353_batch2.xlsx"),
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2016/04/PXD002353/07182013A520SHIHbatch3.xlsx", DATA_DIR / "proteomics" / "PXD002353_batch3.xlsx"),
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2016/04/PXD001815/PXD001815_community_annotated.sdrf.tsv", DATA_DIR / "proteomics" / "PXD001815.sdrf.tsv"),
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2016/04/PXD002353/PXD002353_community_annotated.sdrf.tsv", DATA_DIR / "proteomics" / "PXD002353.sdrf.tsv"),
        ("https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/12/PXD031138/PXD031138_community_annotated.sdrf.tsv", DATA_DIR / "proteomics" / "PXD031138.sdrf.tsv"),
    ]
    for url, dest in comp_urls:
        manifest_log.append(download_file(url, dest, max_mb=50.0))

    log_path = DATA_DIR / "download_manifest_log.json"
    log_path.write_text(json.dumps(manifest_log, indent=2))
    print(f"\n=== Completed downloads. Log written to {log_path} ===")


if __name__ == "__main__":
    main()
