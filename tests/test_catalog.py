from pathlib import Path
import json
import csv
import pytest
from atmos_catalog.catalog import (
    normalize_pressure,oxygen_partial_pressure,canonical_alias,build,validate,sample_audit)
from atmos_catalog.http import MetadataClient,check_metadata_url

REPO=Path(__file__).resolve().parents[1]

def test_pressure_and_missing_units():
    assert normalize_pressure(8.2,"psia")==pytest.approx(56.5370098039776)
    assert normalize_pressure(101325,"Pa")==pytest.approx(101.325)
    assert normalize_pressure(50,None) is None
    assert normalize_pressure(50,"kPa",basis="gauge") is None
    assert normalize_pressure(None,"kPa") is None
    assert normalize_pressure(50,"unknown") is None
    with pytest.raises(ValueError):normalize_pressure(-1,"kPa")

def test_po2_does_not_conflate_fraction_with_hyperoxia():
    assert oxygen_partial_pressure(normalize_pressure(8.2,"psia"),.34)==pytest.approx(19.222583333352386)
    assert oxygen_partial_pressure(50,.42)==21
    assert oxygen_partial_pressure(None,.04) is None
    with pytest.raises(ValueError):oxygen_partial_pressure(50,42)

def test_known_aliases():
    assert canonical_alias("GLDS-134")=="OSD-134"
    assert canonical_alias("E-GEOD-87867")=="GSE87867"
    assert canonical_alias("GSE87867")!="GSE87903"

@pytest.mark.parametrize("url",[
    "https://example.org/metadata","http://www.ncbi.nlm.nih.gov/",
    "https://www.ncbi.nlm.nih.gov/file.fastq.gz",
    "https://zenodo.org/records/16536514/files/example.xlsx",
    "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9251057&view=full&targ=self"])
def test_download_and_host_guards(url):
    with pytest.raises(ValueError):check_metadata_url(url)

def test_brief_metadata_allowed():
    check_metadata_url("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9251057&view=brief&targ=self")

def test_offline_never_networks(tmp_path):
    c=MetadataClient(tmp_path,offline=True)
    with pytest.raises(FileNotFoundError):c.get("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi",{"acc":"GSE87867"})

def test_real_snapshot_design_anomalies():
    snapshot=json.loads((REPO/"data/snapshot/public_facts_2026-10-15.json").read_text())
    rows=sample_audit(snapshot)
    assert len([r for r in rows if r["organ_conflict"]])==4
    one=[r for r in rows if r["study_id"]=="GSE87904" and r["sample_id"]=="GSM2342816"][0]
    assert one["duration_hours"]==1
    conflicts=[r for r in rows if r["sample_id"]=="GSM2342806"]
    assert all(r["organ"].startswith("unresolved") for r in conflicts)
    nuclei=[r for r in rows if r["study_id"]=="GSE308672"]
    assert len(nuclei)==4 and all(r["pressure_kpa"] is None for r in nuclei)
    shared=[r for r in rows if r["sample_id"]=="GSM2342067"]
    assert {r["study_id"] for r in shared}=={"GSE87867","GSE87903"}
    assert len(snapshot["osdr"][0]["sample_crosslinks"])==33

def test_frozen_build_deterministic(tmp_path):
    a=tmp_path/"a";b=tmp_path/"b"
    ma=build(REPO,a);mb=build(REPO,b)
    assert ma==mb
    assert ma["unique_hypobaria_gsms"]==130
    assert ma["master_records"]==22 and ma["validated_records"]==16
    for file in a.glob("*.csv"):
        assert file.read_bytes()==(b/file.name).read_bytes()
    assert validate(REPO,a)["status"]=="passed"
    with (a/"file_manifest.csv").open() as f:files=list(csv.DictReader(f))
    assert len({r["filename"] for r in files if r["study_id"]=="ZENODO16536514"})==7
    assert {r["assay_id"] for r in files if r["study_id"]=="PXD001815"}=={"PXD001815","PXD002353"}

def test_real_discovery_pagination_and_failure_semantics(tmp_path,monkeypatch):
    from atmos_catalog import discovery
    snapshot=json.loads((REPO/"data/snapshot/public_facts_2026-10-15.json").read_text())
    counts={}
    for c in snapshot["candidate_occurrences"]:
        if c["repository"]=="GEO":
            counts.setdefault(c["query"],[]).append(c["accession_or_uid"])
    query,real_uids=max(counts.items(),key=lambda x:len(x[1]))
    assert len(real_uids)==337
    # Reconstruct protocol responses from the actual recorded UID list.
    calls=[]
    def recorded_page(self,url,params=None,**kwargs):
        start=params["retstart"];calls.append(start)
        return json.dumps({"esearchresult":{"count":str(len(real_uids)),
            "idlist":real_uids[start:start+params["retmax"]]}}),{
            "http_status":200,"url":url,"retrieved_utc":"2026-10-15"}
    monkeypatch.setattr(discovery.MetadataClient,"get",recorded_page)
    config={"jobs":[{"kind":"entrez","label":"recorded337","repository":"GEO","db":"gds","query":query}],
            "page_size":100,"max_pages":20}
    ledger,candidates=discovery.run_discovery(config,tmp_path/"cache",tmp_path/"pages")
    assert calls==[0,100,200,300] and len(candidates)==337
    assert all(r["status"]=="complete" for r in ledger)
    config["max_pages"]=1
    ledger,_=discovery.run_discovery(config,tmp_path/"cache",tmp_path/"truncated")
    assert ledger[-1]["status"]=="truncated"
    def failed(self,url,params=None,**kwargs):
        return "",{"http_status":503,"url":url,"retrieved_utc":"2026-10-15"}
    monkeypatch.setattr(discovery.MetadataClient,"get",failed)
    ledger,candidates=discovery.run_discovery(config,tmp_path/"cache",tmp_path/"failed")
    assert ledger[0]["status"]=="failed"
    assert ledger[0]["retrieved_records"] is None and not candidates

def test_redirect_cannot_escape_allowlist(tmp_path,monkeypatch):
    class Redirect:
        status_code=302
        headers={"Location":"https://example.org/not-approved"}
        def close(self):pass
    c=MetadataClient(tmp_path,delay=0)
    seen=[]
    def request(url,**kwargs):
        seen.append(url)
        return Redirect()
    monkeypatch.setattr(c.session,"get",request)
    monkeypatch.setattr("atmos_catalog.http.time.sleep",lambda _:None)
    _,meta=c.get("https://www.ncbi.nlm.nih.gov/")
    assert all(url=="https://www.ncbi.nlm.nih.gov/" for url in seen)
    assert meta["http_status"]==0 and meta["error"]

def test_build_never_accesses_network(tmp_path,monkeypatch):
    def forbidden(*args,**kwargs):
        raise AssertionError("Offline build attempted network access")
    monkeypatch.setattr(MetadataClient,"get",forbidden)
    assert build(REPO,tmp_path/"offline")["validated_records"]==16

def test_report_pair_complete_text_and_tables(tmp_path):
    from atmos_catalog.reporting import report,validate_report_pair
    build(REPO,tmp_path/"tables")
    report(REPO,tmp_path/"reports",tmp_path/"tables")
    stem=tmp_path/"reports/report_arabidopsis_exploration_atmosphere"
    checks=validate_report_pair(stem.with_suffix(".md"),stem.with_suffix(".docx"))
    assert checks["all_text_and_tables_match_markdown"]
    assert checks["word_tables"]==5 and checks["word_hyperlinks"]==29
