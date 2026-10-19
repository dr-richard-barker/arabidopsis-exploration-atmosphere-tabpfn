# Arabidopsis exploration-atmosphere omics

Public-data catalog and feasibility audit | Version 0.1.0 | 16 October 2026

Author: Richard John Barker. Prepared with Biomni. Metadata-only discovery and design review; no biological measurements were downloaded or reanalyzed.

## Executive summary

The strongest available route is to reanalyze the oxygen-supplemented hypobaria microarrays first, then use independent oxygen-treated nuclei to examine mechanistic overlap and untreated plant atlases to generate localization hypotheses. No exact NASA nominal-atmosphere Arabidopsis omics experiment, or low-pressure-treated single-cell/nucleus experiment, was verified within the searched coverage. This is a bounded search finding, not proof that such data do not exist.

The curated MASTER catalog contains **22 canonical experiment/reference/lead records**, including **16 validated records**, five direct pressure-related experiments, three weaker leads and three explicit exclusions. “Validated” means identity, modality, relevance and public availability are supported; it does not imply complete covariates, sufficient replication, matrix quality control or readiness for differential expression. Four 2017 hypobaria GEO subseries contain **148 sample memberships but only 130 unique GSM array records** because 18 arrays are shared across the two publications. SuperSeries wrappers and OSD/GLDS aliases do not add independent studies.

A 2025 deposit provides independent low-pressure metabolite/physiology files at 101 versus 62 kPa, but its public description does not establish oxygen conditions or specimen-level matching across files. A 2026 root snRNA-seq experiment directly measures 21% versus 4% oxygen responses, not pressure responses. Neither can be represented as a sample-matched multiomics extension of the 2017 arrays. [64](https://zenodo.org/records/16536514), [79](https://pmc.ncbi.nlm.nih.gov/articles/PMC12917472/)

## Methods and search coverage

Discovery covered all years available through the retrieval date. Organism-constrained terms included hypobaric/hypobaria, reduced/low atmospheric pressure, exploration atmosphere, oxygen enrichment, hyperoxia/hypoxia, and relevant bulk, single-cell/nucleus, metabolomic, proteomic and epigenomic assays. OSDR keyword searches were supplemented by an organism-wide assay listing; GEO and SRA searches by ENA and BioStudies; and proteomics/metabolomics discovery by PRIDE, OmicsDI and targeted repository web searches. Plant atlas portals were preferred over human/cancer resources. The Salk plant portal was reviewed rather than assuming that the central human/mouse Census covered Arabidopsis. [31](https://neomorph.salk.edu/ada/)

The release preserves **45 API search-page records**, **23 supplemental web-search queries**, **485 candidate occurrences**, **146 unique sample metadata extracts**, **164 study-by-sample audit rows** and **1952 file inventory records**. Candidate occurrences are not unique eligible studies. Repeated studies across queries and aggregators are intentionally visible in the discovery ledger. Four priority hypobaria subseries and all four treated-nucleus libraries were audited at sample level; two representative samples per additional GEO comparator/atlas were inspected, not a complete sample audit of every reference.

Only metadata views, factual extracts and file inventories were retrieved. GEO GSM requests used self/brief views to avoid expression tables. Series-self records supplied sample IDs and file links. No CEL, FASTQ, count matrix, RDS, H5AD, metabolite workbook or measurement table was downloaded. Live discovery uses a host allowlist, bounded retries, rate limiting, response-size caps and private caching. Offline build, validation and report generation use the frozen, sanitized public-fact snapshot and versioned curation decisions.

| Repository/interface | Coverage outcome |
|---|---|
| GEO, SRA, ENA, BioStudies, OmicsDI | Query pages retained; GEO title-query translation broadened one query to 337 hits. All hits are not confirmed relevant. |
| OSDR | Two hypobaria mirrors confirmed: OSD-134 and OSD-136. File API is one-based; page-0 false-empty results were corrected. |
| PRIDE / ProteomeXchange | Initial project-list keyword filter was ineffective. Corrected search endpoint returned empty lists for two combined queries; known-accession and independent web discovery recovered adjacent studies. |
| Zenodo | API returned 403; public version-specific HTML yielded the seven-file low-pressure deposit. |
| MetaboLights, Workbench, Expression Atlas | API failure, unvalidated response schema or unavailable response; none is interpreted as evidence of zero datasets. |
| Figshare, Dryad, OSF, Dataverse, MassIVE/GNPS, jPOST/iProX | Targeted indexed web searches/aggregator discovery, not exhaustive repository crawls; no additional directly eligible pressure omics deposit verified. |

The source and search ledgers retain exact queries/URLs, dates, HTTP/schema outcomes and checksums where available. Manual web-query timestamps are date-resolution; raw API request provenance is UTC. The catalog is an exploratory, provenance-audited research resource, not a systematic review. Access restrictions were noted, not bypassed.

## NASA target and the pressure–oxygen distinction

NASA's nominal exploration atmosphere is **8.2 psia and 34% oxygen**, distinct from the historical 8.0 psia/32% variant and staged 10.2 psia/26.5% atmosphere. [3](https://ntrs.nasa.gov/citations/20150021491), [5](https://ntrs.nasa.gov/citations/20230015380)

Using 1 psi = 6.894757293168 kPa gives 56.537 kPa total absolute pressure. The dry chamber estimate pO2 = pressure × oxygen fraction is 19.223 kPa. Thus oxygen enrichment by fraction does not imply elevated oxygen partial pressure relative to approximately 21 kPa terrestrial ambient oxygen. These are chamber calculations, not plant tissue oxygen measurements; human inspired/alveolar corrections are inappropriate here.

| Atmosphere or study setpoint | Total pressure | O2 fraction | Chamber pO2 |
|---|---|---|---|
| NASA nominal | 56.54 kPa, derived | 34%, reported | 19.22 kPa, derived |
| 2017 supplemented moderate hypobaria | 50 kPa, reported | 42%, derived | 21 kPa, reported |
| 2017 supplemented severe hypobaria | 25 kPa, reported | 84%, derived | 21 kPa, reported |
| 2017 low-oxygen ambient-pressure control | 97 kPa, reported | 5.26%, derived | 5.1 kPa, GEO; paper rounds to 5 |
| 2025 independent deposit | 62 versus 101 kPa | Not established | Not established |

The 50 kPa/21 kPa-pO2 condition is adjacent to, not equivalent to, the NASA mixture: it is 6.54 kPa lower in total pressure and has an inferred oxygen fraction eight percentage points higher. No arbitrary “close enough” matching tolerance was imposed. Reported and derived values remain separate in the audit. The pressure-gradient paper reports nominal 21% oxygen but also calls ambient 97 kPa pO2 approximately 21 kPa; 97 × 0.21 = 20.37 kPa. Both statements are preserved rather than silently harmonized. [13](https://doi.org/10.3389/fpls.2017.00528), [15](https://doi.org/10.1093/aobpla/plx030)

## Direct atmospheric datasets and design audit

| Canonical record | Deposited design | Feasible future comparison |
|---|---|---|
| GSE87867 / OSD-134 | 10-day WS roots/shoots; six pressure–pO2 conditions; 24 h; 33 arrays | Pressure at approximately restored pO2; oxygen effects at fixed 50 or 25 kPa, with group-level limitations |
| GSE87868 / OSD-136 | 5-day WS roots; 97/21, 50/10, 50/21 kPa total/pO2; 24 h; 9 arrays | Young-root pressure and oxygen contrasts; three deposited arrays/group |
| GSE87903 | 10-day-start WS roots/shoots; 97–5 kPa gradient; 24 h; 34 arrays | Combined pressure/hypoxia gradient; not isolated pressure |
| GSE87904 | WS roots/shoots; 10 versus 97 kPa; 1,3,6,12,48,72 h; 72 arrays | Organ-by-time response to combined pressure/hypoxia |
| Zenodo 16536514 v2 | 101 versus 62 kPa; shoot metabolites and physiology; seven XLSX files | Independent low-pressure biochemical comparison after missing design metadata are resolved |

The four GEO subseries are ATH1 **microarrays**, not bulk RNA-seq. OSDR/GEO sample cross-links confirm OSD-134 = GSE87867 and OSD-136 = GSE87868. Accession proximity is not evidence of linkage: OSD-135 and OSD-137 were checked and excluded because they are mouse studies. The gradient/time-course accessions were retained as GEO studies without inventing OSDR mirrors. [13](https://doi.org/10.3389/fpls.2017.00528), [15](https://doi.org/10.1093/aobpla/plx030)

### Sample identity, replication and unresolved annotations

The shared 18 GSMs are the 97, 50 and 25 kPa unsupplemented root/shoot arrays in GSE87867 and GSE87903. They must not be counted twice in a meta-analysis or treated as an independent replication of the earlier paper. GSE87869, GSE87905 and GSE14578 are SuperSeries wrappers and are recorded only as relationships, not independent experiments.

GSE87867 is not a uniformly three-replicate design. Deposited root groups have 3,3,3,2,1,3 arrays for 97/21, 50/10, 25/5, 50/21, 25/21 and 97/5.1 respectively. Shoot counts are 3,3,3,4,3,2 in the same order. A single root array at 25/21 cannot support a conventional within-group variance estimate. The fourth shoot array at 50/21 is not automatically a fourth independent chamber. Pooling and chamber-to-array identities must be resolved before inferential modeling. Sample-level evidence is retained in the condition audit, including [GSM2342078](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2342078) and [GSM2342094](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2342094).

All nine GSE87868 sample tissue fields specify **roots**; a five-day shoot experiment must not be inferred from the broad study abstract. In GSE87903, four 75 kPa arrays, GSM2342806–GSM2342809, say “Shoot” in their titles but “Roots” in their tissue characteristics. The audit leaves these organs explicitly unresolved. GEO age fields also mix 10 and 11 days versus the paper's 10-day exposure start; start versus harvest age needs harmonization. By title there is no deposited root 5 kPa group. See the conflicting [GSM2342806](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2342806) record; no silent correction was made.

GSE87904 provides three array records per organ/pressure/time group. Its 24 h point comes from the separate gradient experiment, not an independently repeated time-course point. The 2017 experiments report independent chambers, constant pCO2 of 0.05 kPa, hydrated agar plates, high plate humidity and continuous light, but raw array records remain distinct from demonstrated independent chamber replicates. [13](https://doi.org/10.3389/fpls.2017.00528), [15](https://doi.org/10.1093/aobpla/plx030)

The gradient/time-course publication contains an analysis caveat: methods discuss Benjamini–Hochberg correction, whereas the text explains use of unadjusted P because FDR obscured contrasts. Its reported nominal P < 0.01 and absolute log2 fold change > 1 lists must not be called FDR-significant. Future reanalysis should estimate effects and uncertainty with explicit multiplicity control rather than reuse the published gene counts as definitive evidence. [15](https://doi.org/10.1093/aobpla/plx030)

The 2025 Zenodo deposit is independent of these arrays. It contains shoot metabolite identification/profiling, gas exchange, chlorophyll fluorescence, growth, pigment, nitrogen/d13C and chamber CO2 workbooks. Public metadata leave ecotype, age, duration, oxygen conditions and biological replicate correspondence unresolved. File descriptions do not establish whether metabolite entries contain quantitative abundance, identifications alone, or both; that requires later authorized workbook inspection. The v1 and concept DOIs are aliases of the same versioned deposit, not extra experiments. [64](https://zenodo.org/records/16536514)

## Oxygen-related and multiomics comparators

| Record | Biological/assay evidence | Integration boundary |
|---|---|---|
| GSE308672 | 5-day Col-0 root tips; 21% versus 4% O2; 4 h dark; 2 biological replicates/group; snRNA-seq | Direct cell-resolved hypoxia evidence, not hypobaria or NASA-mixture evidence |
| GSE11558 | Roots; 21/8/4/1% O2; 0.5/2/48 h; arrays and GC-MS reported | Same-study layers, but reusable metabolite matrix and specimen matching unverified |
| GSE14493 / GSE14502 | Hypoxia/control TRAP and total RNA microarrays; root tips and root/shoot populations | Ribosome-associated RNA, not protein abundance and not single-cell sequencing |
| E-MTAB-11231 / PXD031138 | Ethylene–hypoxia–recovery root transcriptome; ethylene-versus-air TMT proteome | Same publication, different treatment/age designs; no specimen pairing established |
| PXD001815 / PXD002353 | 9-day whole seedlings; Col-0/SnRK1.1K48M; 0–3 h submergence; phospho/total proteomes | Companion assays retained under one study; specimen mapping still needed; submergence is not pure gas hypoxia |

GSE308672 is the highest-priority treated single-nucleus comparator. Each biological replicate pooled at least 50 plants across five plates. The deposited protocol specifies 10x 3-prime v3.1 dual index, scKB against TAIR10, COPILOT quality control and Seurat label transfer from the Shahan root atlas. Per-library filtered sparse counts and an integrated Seurat RDS are listed; no matrix was inspected. Two replicates/group limit inference, especially for rare cells. Future differential testing should aggregate raw counts by biological replicate and cell type, not treat thousands of nuclei as independent experimental units or test integrated assay values as counts. [79](https://pmc.ncbi.nlm.nih.gov/articles/PMC12917472/), [GEO sample](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9251057)

GSE11558 supports mild-oxygen mechanistic comparison rather than pressure specificity. Two inspected GEO samples identify Col-2, not the WS pressure-study ecotype. The paper reports parallel GC-MS profiling, but this audit verifies a GEO array deposit, not a standalone downloadable GC-MS abundance matrix. TRAP studies provide cell-population-enriched translationally associated mRNA; their 99 combined arrays are not 99 cell types or sequenced cells. [61](https://doi.org/10.1093/aob/mcn126), [62](https://doi.org/10.1073/pnas.0906131106)

PXD031138 documents five biological replicates per ethylene/air treatment in a TMT10plex design; LC fractions and SDRF rows are not additional biological replicates. Its linked E-MTAB-11231 contains a separate 44-sample transcriptomic ethylene–hypoxia–recovery design, including nitrogen flushing that reaches near-zero oxygen. The proteomics samples must not be relabeled hypoxia-treated merely because the paper studies hypoxia tolerance. PXD001815/PXD002353 retain both complementary phosphoproteome and total-proteome file sets; the total-proteome protocol reports three biological experiments with technical repeats, which must not automatically be assigned to every phosphosite contrast. [88](https://www.ebi.ac.uk/pride/archive/projects/PXD031138), [BioStudies metadata](https://www.ebi.ac.uk/biostudies/api/v1/studies/E-MTAB-11231), [127](https://www.ebi.ac.uk/pride/archive/projects/PXD001815), [131](https://www.ebi.ac.uk/pride/archive/projects/PXD002353)

No verified directly matched pressure transcriptome/proteome/metabolome cohort was found. Cross-study pathway concordance may be reasonable later; concatenating unrelated sample matrices or presenting a joint latent factor as a matched biological multiomics response would not be justified.

## Cell-type and organ reference suitability

| Reference | Useful coverage | Main limitation |
|---|---|---|
| GSE226097 / Salk developmental atlas | 432,919 nuclei; 3/6/12-day seedlings plus seeds, rosettes, stems and reproductive organs; TAIR10+Araport11; stage-specific RDS | Untreated Col-0 reference; 84 GEO records are not 84 biological replicates; spatial panels cover selected genes |
| GSE152766 / Shahan root atlas | Root types/states; TAIR10; counts and Seurat objects; annotation bridge to treated nuclei | Restrict WT reference; exclude developmental mutants and deduplicate three reused WT samples |
| PRJNA742744 / Apelt atlas | 7-day roots; five-week shoots at end of day/night; Drop-seq and reference RNA libraries | Root/shoot ages differ; three root preparations are different reporter lines; standalone matrix availability not confirmed |
| PXD013868 | Baseline tissue proteome/phosphoproteome context | Tissue-level, not single-cell and not atmospheric treatment |
| CNP0002614 | Advertised six-day shoots and 6/11-day roots among20 tissues | Lead only; primary annotation, replication and rights need further audit |

The Salk atlas is the preferred broad seedling reference for a future WS bulk-response signature. It has at least two independently prepared biological replicates per stage, split across multiple technical loadings. Proximity of stage is useful but does not remove ecotype, photoperiod, growth-medium, organ-mixture or nuclei-versus-cell bias. A cell type with high baseline expression of a bulk-response gene is not necessarily the cell type in which its atmospheric response occurs. [32](https://doi.org/10.1038/s41477-025-02072-z)

The Shahan assembled atlas includes 18 WT, two scr-4 and two shr-2 samples; three WT samples originate in GSE123818/GSE123013, leaving 19 newly deposited GSM records. Reused samples must not inflate independent atlas support. Representative sample metadata specify TAIR10 and COPILOT-processed count/Seurat formats. [GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152766), [GEO sample](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4625993)

The Apelt study's three root reporter preparations are not interchangeable with three identical-genotype root replicates. Its shoot samples represent differentiated five-week tissue rather than the ten-day pressure-treated seedlings. The study's protoplasting controls and diurnal design are useful specifically for assessing those biases. Baseline atlas data measure expression location; only a treatment/control design directly measures differential response. [126](https://pmc.ncbi.nlm.nih.gov/articles/PMC8825464/)

## Gaps, interpretation and recommended next steps

- **Exact atmosphere gap:** no verified nominal 56.5 kPa/34% oxygen omics design. The 50 kPa/21 kPa-pO2 arrays are the nearest oxygen-supplemented pressure design in this catalog, not a nominal match.
- **Cell-treatment gap:** root hypoxia nuclei exist, but no low-pressure-treated single-cell/nucleus data were verified. There is no equivalent verified shoot cell-resolved pressure treatment.
- **Organ/stage gap:** direct pressure transcriptomes emphasize WS seedling roots/shoots; young treatment is roots only. Reproductive and mature leaf atlas coverage does not fill that treated-organ gap.
- **Multiomics gap:** independent low-pressure metabolite files and oxygen-related proteomics exist, but specimen-matched pressure multiomics is not established. No direct pressure epigenomic deposit was verified.
- **Metadata gap:** chamber-to-array maps, four organ-label conflicts, age basis, old probe mappings and complete comparator sample designs need resolution before analysis.
- **Search gap:** API failures, literal keyword behavior, aggregator lag and unindexed supplements prevent exhaustive negative conclusions. The historical 2004 8K-array pressure study remains a supplement-only lead without a verified reusable omics accession. [12](https://pmc.ncbi.nlm.nih.gov/articles/PMC316301/)

1. **Resolve design annotations before retrieving measurements.** Confirm the four75 kPa tissue conflicts, independent chamber identities and array exclusions with source supplements or authors; obtain the independent62 kPa experiment's oxygen and specimen map.
2. **Reanalyze the ATH1 studies as one provenance-aware resource.** With separate authorization, download raw arrays; verify CEL identity/QC; map probes to a documented TAIR/Araport release; preserve shared GSMs and unbalanced groups; model only identifiable effects with multiple-testing control. Avoid a confident n=1 root25/21 contrast.
3. **Analyze treated root nuclei independently.** With authorized counts and annotations, assess replicate-level cell-type coverage, then pseudobulk hypoxia versus normoxia. Compare effect directions or pathways to bulk hypobaria without asserting the same physical stimulus.
4. **Localize a validated bulk signature using stage-matched WT atlases.** Prefer seedling subsets of the Salk atlas, with Shahan as the root-state reference. Report baseline localization as inferred, not measured cell-specific pressure response; use shoot atlases with explicit age/diurnal caveats.
5. **Expand multiomics only after pairing is verified.** Inspect the independent metabolite workbook and linked proteome/transcriptome maps before choosing integration. If an exact exploration-atmosphere answer is required, design a new pressure-by-pO2 experiment with independent chambers, controlled CO2/light/RH and matched samples.

## Reproducibility, release contents and rights

The Python interface provides `discover`, `build`, `validate`, `report` and `package`. Frozen builds are network-free; live discovery is an explicit opt-in that writes a new dated review directory and never silently overwrites curated release decisions. Refreshing discovery does not automatically validate new hits. The snapshot, curation files, tests, dependency pins, data dictionary and source-rights notes are included.

Full CSVs contain the MASTER/VALIDATED catalogs, study and sample condition audits, condition groups, file inventory, atlas suitability, accession relationships, search/provenance ledgers and optional-lead decisions. Empty fields mean missing/unresolved, never zero. File manifest entries are inventories, not downloaded data. File counts, runs, array/library records, cells and independent biological samples are distinct quantities.

Original code is MIT licensed. Original report text, catalog organization and annotations are CC BY 4.0; these licenses do not relicense third-party source records, data or publications. Richard John Barker is the release author; no affiliation, ORCID or DOI has been invented. Zenodo citation/deposition metadata are prepared locally only. No remote repository, upload, publication or DOI reservation was performed. The release is a metadata catalog with supporting software, not a biological reanalysis.
