"""
Builds the GitHub Pages website for the Arabidopsis Exploration Atmosphere TabPFN study.
Uses CoSE / Cayman style and layout (responsive single-column layout, vibrant teal gradient hero,
clean typography, card components, interactive modal figure gallery, no sidebar).
"""
from pathlib import Path

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
DOCS_DIR = PROJECT_DIR / "docs"
CSS_DIR = DOCS_DIR / "assets" / "css"
FIG_DIR = DOCS_DIR / "figures"


def generate_css():
    css_content = """/* CoSE / Cayman Responsive Theme (No Sidebar) */
:root {
  --primary-color: #0d3b66;
  --secondary-color: #008080;
  --accent-color: #e74c3c;
  --accent-gold: #f39c12;
  --text-color: #2c3e50;
  --text-muted: #606f7b;
  --bg-color: #ffffff;
  --bg-alt: #f8fafc;
  --border-color: #e2e8f0;
  --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --hero-gradient: linear-gradient(135deg, #0d3b66 0%, #157878 50%, #008080 100%);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--text-color);
  background-color: var(--bg-color);
  line-height: 1.65;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}

/* Hero Header */
.page-header {
  background: var(--hero-gradient);
  color: #ffffff;
  text-align: center;
  padding: 4rem 1.5rem 3.5rem;
  box-shadow: inset 0 -3px 8px rgba(0,0,0,0.2);
}

.page-header .project-title {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1.25;
  margin-bottom: 1rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  letter-spacing: -0.02em;
}

.page-header .project-tagline {
  font-size: 1.2rem;
  font-weight: 400;
  opacity: 0.92;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.65rem 1.35rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
}

.btn:hover {
  background-color: #ffffff;
  color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.btn-primary {
  background-color: #e74c3c;
  border-color: #e74c3c;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #c0392b;
  color: #ffffff;
}

/* Metric Strip */
.metric-strip {
  background-color: var(--bg-alt);
  border-bottom: 1px solid var(--border-color);
  padding: 1.8rem 1rem;
}

.metric-container {
  max-width: 1060px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1.2rem;
  text-align: center;
}

.metric-card {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.2rem 1rem;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--secondary-color);
  margin-bottom: 0.3rem;
  line-height: 1.1;
}

.metric-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Main Container (Single-column layout, NO sidebar) */
.main-content {
  max-width: 1060px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}

/* Typography & Headings */
h2.section-heading {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-top: 3rem;
  margin-bottom: 1.2rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

h3.sub-heading {
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--secondary-color);
  margin-top: 1.8rem;
  margin-bottom: 0.8rem;
}

p {
  margin-bottom: 1.2rem;
  font-size: 1.02rem;
  color: #334155;
}

/* Callout Alert */
.alert-box {
  background-color: #ecf9f6;
  border-left: 4px solid var(--secondary-color);
  padding: 1.2rem 1.5rem;
  border-radius: 0 8px 8px 0;
  margin: 1.8rem 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.alert-box strong {
  color: var(--secondary-color);
  display: block;
  margin-bottom: 0.4rem;
  font-size: 1.05rem;
}

/* Workpackage Cards */
.wp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.wp-card {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1.6rem;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  transition: all 0.25s ease;
}

.wp-card:hover {
  border-color: var(--secondary-color);
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
  transform: translateY(-3px);
}

.wp-badge {
  display: inline-block;
  align-self: flex-start;
  padding: 0.25rem 0.75rem;
  background-color: #e6fffa;
  color: var(--secondary-color);
  border: 1px solid #b2f5ea;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
}

.wp-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.6rem;
  line-height: 1.35;
}

.wp-desc {
  font-size: 0.92rem;
  color: #475569;
  flex-grow: 1;
  margin-bottom: 1rem;
}

.wp-stats {
  border-top: 1px solid #f1f5f9;
  padding-top: 0.8rem;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

/* Figures Section */
.figures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.figure-card {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
}

.figure-card img {
  width: 100%;
  height: 240px;
  object-fit: contain;
  background-color: #f8fafc;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  transition: transform 0.2s ease;
}

.figure-card img:hover {
  transform: scale(1.02);
}

.figure-body {
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.figure-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.4rem;
}

.figure-caption {
  font-size: 0.88rem;
  color: #64748b;
  line-height: 1.45;
  margin-bottom: 1rem;
  flex-grow: 1;
}

.figure-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 0.6rem;
}

.figure-footer a {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--secondary-color);
  text-decoration: none;
}

.figure-footer a:hover {
  text-decoration: underline;
}

/* Data & Notebook Tables */
.table-container {
  overflow-x: auto;
  margin: 1.8rem 0;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  background: #ffffff;
}

th {
  background-color: #f1f5f9;
  color: var(--primary-color);
  font-weight: 700;
  text-align: left;
  padding: 0.85rem 1rem;
  border-bottom: 2px solid var(--border-color);
}

td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  color: #334155;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: #f8fafc;
}

/* Modal Lightbox */
.modal {
  display: none;
  position: fixed;
  z-index: 1000;
  padding-top: 40px;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.88);
}

.modal-content {
  margin: auto;
  display: block;
  max-width: 90%;
  max-height: 85vh;
  border-radius: 6px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.modal-caption {
  margin: auto;
  display: block;
  width: 80%;
  max-width: 900px;
  text-align: center;
  color: #f1f5f9;
  padding: 1rem 0;
  font-size: 1rem;
  font-weight: 500;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 35px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
}

.modal-close:hover {
  color: var(--accent-gold);
}

/* Footer */
footer.site-footer {
  background-color: var(--primary-color);
  color: #cbd5e1;
  padding: 3rem 1.5rem;
  font-size: 0.9rem;
  border-top: 3px solid var(--secondary-color);
}

.footer-content {
  max-width: 1060px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 2rem;
}

.footer-col {
  flex: 1 1 280px;
}

.footer-col h4 {
  color: #ffffff;
  font-size: 1.05rem;
  margin-bottom: 0.8rem;
  font-weight: 700;
}

.footer-col p {
  color: #94a3b8;
  font-size: 0.88rem;
}

.footer-col a {
  color: #38bdf8;
  text-decoration: none;
}

.footer-col a:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header .project-title {
    font-size: 1.8rem;
  }
  .page-header .project-tagline {
    font-size: 1rem;
  }
  .main-content {
    padding: 2rem 1rem 3rem;
  }
}
"""
    (CSS_DIR / "style.css").write_text(css_content)
    print(f"Generated {CSS_DIR / 'style.css'}")


def generate_index_html():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Arabidopsis Exploration Atmosphere | TabPFN v2 Foundation Model Decoupling</title>
  <meta name="description" content="Decoupling Total Barometric Pressure from Oxygen Partial Pressure in the Arabidopsis thaliana Spaceflight Exploration Atmosphere Using the TabPFN v2 Tabular Foundation Model">
  <link rel="stylesheet" href="assets/css/style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
</head>
<body>

  <!-- CoSE Cayman-Style Hero Banner (No Sidebar) -->
  <header class="page-header" role="banner">
    <div class="project-title">Decoupling Total Barometric Pressure from Oxygen Partial Pressure in the <em>Arabidopsis</em> Spaceflight Exploration Atmosphere</div>
    <div class="project-tagline">
      A 12-Dataset Multi-Omics Compendium & TabPFN v2 Tabular Foundation Model Synthesis Resolving Molecular Hubs, Single-Nucleus Trajectories, and Physiological Rescue for NASA's 56.54 kPa / 34% O₂ Habitat
    </div>
    <div class="hero-actions">
      <a href="https://github.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn" class="btn btn-primary" target="_blank">
        <svg height="18" width="18" viewBox="0 0 16 16" fill="currentColor" style="vertical-align: middle;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
        GitHub Repository
      </a>
      <a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/manuscript_exploration_atmosphere_tabpfn.docx" class="btn">
        📄 Download Manuscript (.docx)
      </a>
      <a href="#workpackages" class="btn">🔬 5 Workpackages</a>
      <a href="#figures" class="btn">📊 6 Publication Figures</a>
      <a href="#notebooks" class="btn">📓 Jupyter Notebooks</a>
    </div>
  </header>

  <!-- Metric Highlights Strip -->
  <div class="metric-strip">
    <div class="metric-container">
      <div class="metric-card">
        <div class="metric-value">130</div>
        <div class="metric-label">Harmonized Arrays (22,746 Probes)</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">40,860</div>
        <div class="metric-label">Single-Nucleus Root Profiles</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">0.9134</div>
        <div class="metric-label">TabPFN v2 R² (Pressure Regression)</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">380 vs 1,243</div>
        <div class="metric-label">Pure Baro vs. Hypoxia Hubs</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">70–75% RH</div>
        <div class="metric-label">Atmospheric Rescue Setpoint</div>
      </div>
    </div>
  </div>

  <!-- Single-Column Main Content (NO SIDEBAR) -->
  <main class="main-content" id="content">

    <section id="overview">
      <h2 class="section-heading">🌌 Executive Summary & Scientific Context</h2>
      <p>
        Future crewed lunar and Martian surface habitats, extravehicular activity (EVA) staging airlocks, and bioregenerative life-support systems (BLSS) will operate under NASA's reduced-pressure, oxygen-enriched <strong>Exploration Atmosphere</strong>:
        <strong>56.54 kPa (8.2 psia) at 34% O₂</strong> (normoxic oxygen partial pressure <em>pO₂</em> = 19.22 kPa) and a staged pre-EVA setpoint of <strong>70.33 kPa (10.2 psia) at 26.5% O₂</strong> (<em>pO₂</em> = 18.64 kPa).
      </p>

      <div class="alert-box">
        <strong>The Fundamental Biophysical Asymmetry:</strong>
        By the Chapman–Enskog kinetic theory of gases, binary molecular diffusivity scales inversely with total pressure (<em>D ∝ 1/P_total</em>). 
        Reducing cabin pressure to 56.54 kPa accelerates gas and water-vapor diffusion by <strong>1.72×</strong> relative to ISS standard air (97 kPa), stripping the leaf boundary layer and driving acute evaporative demand. 
        While 34% O₂ eliminates crew hypoxia, plants still experience intense physical barosensory stress that oxygen supplementation alone cannot cure.
      </div>

      <p>
        Here, we integrate the <strong>TabPFN v2 tabular foundation model</strong> (Hollmann et al., <em>Nature</em> 637, 319–326, 2025) across a 12-dataset multi-omics compendium spanning 281 microarray hybridizations, 40,860 root-tip single nuclei, 326 whole-plant gas-exchange records, and factorial pressure × humidity LC-MS metabolomics to decouple total barometric pressure from oxygen partial pressure.
      </p>
    </section>

    <!-- Workpackage Section -->
    <section id="workpackages">
      <h2 class="section-heading">🔬 Five-Workpackage System Architecture</h2>
      <div class="wp-grid">

        <div class="wp-card">
          <span class="wp-badge">Workpackage 1</span>
          <div class="wp-title">Forensic Metadata Audit & Organ Classifier</div>
          <div class="wp-desc">
            Deduplicated 18 shared arrays between GSE87867 and GSE87903. 
            Coupled raw Affymetrix CEL headers with TabPFN v2 probabilistic auditing (AUC = 1.0000, Brier = 0.000002) to prove that 4 disputed 75 kPa samples (GSM2342806–809) are Shoots mislabeled as Roots in GEO, corrected 5 kPa root labels, and resolved replicate-A re-hybridizations across scanner batches (r = 0.9951–0.9964).
          </div>
          <div class="wp-stats">130 Unique Arrays • 22,746 Probesets • Table S1</div>
        </div>

        <div class="wp-card">
          <span class="wp-badge">Workpackage 2</span>
          <div class="wp-title">TabPFN v2 Atmospheric Decoupling & Hub Networks</div>
          <div class="wp-desc">
            Benchmarked TabPFN v2 against LightGBM, Random Forest, ElasticNet, and deep MLP under condition-grouped cross-validation. 
            TabPFN v2 (PHE) achieved R² = 0.9134 on continuous hypobaria regression and ROC-AUC = 0.9623 on 4-class regime classification. 
            Exact Shapley attributions separated 1,243 Hypoxia hubs from 380 Pure Barosensory hubs (CMI1, STZ, TCH4, LOX2, ACS6).
          </div>
          <div class="wp-stats">R² = 0.9134 • 380 Barosensory Hubs • Tables S2A–S3</div>
        </div>

        <div class="wp-card">
          <span class="wp-badge">Workpackage 3</span>
          <div class="wp-title">Cell-Type TRAP-seq & Single-Nucleus Mapping</div>
          <div class="wp-desc">
            Mapped atmospheric modules across 19 cell-type TRAP-seq translatomes (GSE14493/14502) and 40,860 root-tip single nuclei (GSE308672). 
            Demonstrated that hypoxia induces ERF-VII anaerobic modules across all 9 root lineages (+2.65 to +3.17 log2CPM), whereas barosensory wax, cuticle, and mechanosensing hubs localize specifically to pCER5 shoot epidermis (+2.21 and +1.21 log2).
          </div>
          <div class="wp-stats">19 Cell Types • 40,860 Single Nuclei • Tables S4A–B</div>
        </div>

        <div class="wp-card">
          <span class="wp-badge">Workpackage 4</span>
          <div class="wp-title">Physiological & Metabolomic Phenotypic Bridge</div>
          <div class="wp-desc">
            Triangulated Ecotron whole-plant gas exchange (ZENODO16536514) at 62 kPa vs 101 kPa, revealing a +73.23% vapor pressure ratio surge driving a -76.25% collapse in stomatal conductance (g_sw) and a -55.93% drop in CO₂ assimilation. 
            Factorial pressure × humidity LC-MS metabolomics proved that 70% RH restores chloroplast oxylipin galactolipids (MGDG-OPDA) and reduces hypobaric state probability from 0.982 to 0.791.
          </div>
          <div class="wp-stats">326 Records • LC-MS Lipids/GSLs • Tables S5A–C</div>
        </div>

        <div class="wp-card">
          <span class="wp-badge">Workpackage 5</span>
          <div class="wp-title">NASA Exploration Atmosphere Counterfactual Synthesis</div>
          <div class="wp-desc">
            Leave-One-Condition-Out (LOCO) validated TabPFN v2 predictions (mean r = 0.7387) for the NASA 56.54 kPa / 34% O₂ setpoint. 
            Counterfactual synthesis proves that 34% O₂ silences >88% of ERF-VII hypoxia induction, but physical barosensory stress (TCH4, LOX2, AOS) persists unabated—confirming that habitat humidity engineering (70–75% RH) is mandatory.
          </div>
          <div class="wp-stats">LOCO r = 0.7387 • Counterfactual Engine • Tables S6A–B</div>
        </div>

      </div>
    </section>

    <!-- Figures Gallery with Lightbox -->
    <section id="figures">
      <h2 class="section-heading">📊 Publication Figures (300 DPI High-Resolution)</h2>
      <p>Click on any figure thumbnail to view in full resolution.</p>

      <div class="figures-grid">

        <div class="figure-card">
          <img src="figures/fig1_data_forensics_harmonization.png" alt="Figure 1: Multi-Study Data Harmonization, Deduplication, and TabPFN v2 Metadata Forensics" onclick="openModal(this.src, 'Figure 1 | Multi-Study Data Harmonization, Deduplication, and TabPFN v2 Metadata Forensics')">
          <div class="figure-body">
            <div class="figure-title">Figure 1: Compendium Forensics & Audit</div>
            <div class="figure-caption">Harmonization of 130 unique hypobaric arrays across P_total vs pO₂ phase space, CEL audit of disputed 75 kPa samples, and TabPFN v2 organ classifier benchmark.</div>
            <div class="figure-footer">
              <a href="figures/fig1_data_forensics_harmonization.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

        <div class="figure-card">
          <img src="figures/fig2_tabpfn_atmospheric_decoupling.png" alt="Figure 2: TabPFN v2 Decouples Barosensory Total Pressure from Oxygen Partial Pressure" onclick="openModal(this.src, 'Figure 2 | TabPFN v2 Decouples Barosensory Total Pressure from Oxygen Partial Pressure')">
          <div class="figure-body">
            <div class="figure-title">Figure 2: Physical Decoupling Benchmark</div>
            <div class="figure-caption">TabPFN v2 out-of-fold continuous regression benchmark (R² = 0.9134 on hypobaria, R² = 0.9733 on hypoxia), 4-class classification, and slice-based error analysis.</div>
            <div class="figure-footer">
              <a href="figures/fig2_tabpfn_atmospheric_decoupling.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

        <div class="figure-card">
          <img src="figures/fig3_molecular_hub_network_shap.png" alt="Figure 3: Identification and SHAP Attribution of Exploration Atmosphere Molecular Hub Nodes" onclick="openModal(this.src, 'Figure 3 | Identification and SHAP Attribution of Exploration Atmosphere Molecular Hub Nodes')">
          <div class="figure-body">
            <div class="figure-title">Figure 3: Molecular Hub Networks & SHAP</div>
            <div class="figure-caption">Orthogonal decomposition of 22,746 transcripts into 1,243 Hypoxia vs 380 Barosensory hubs, global TabPFN v2 SHAP attributions, and oxygen-rescue heatmap across 24 hubs.</div>
            <div class="figure-footer">
              <a href="figures/fig3_molecular_hub_network_shap.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

        <div class="figure-card">
          <img src="figures/fig4_cellular_tissue_localization.png" alt="Figure 4: Cellular and Single-Nucleus Localization of Exploration Atmosphere Signaling Modules" onclick="openModal(this.src, 'Figure 4 | Cellular and Single-Nucleus Localization of Exploration Atmosphere Signaling Modules')">
          <div class="figure-body">
            <div class="figure-title">Figure 4: Single-Nucleus & TRAP Spatial Atlas</div>
            <div class="figure-caption">TRAP-seq translatome enrichment across 19 cell types, 40,860 root-tip single-nucleus hypoxia trajectories, and metabolic sucrose rescue decoupling SnRK1 from ERF-VII.</div>
            <div class="figure-footer">
              <a href="figures/fig4_cellular_tissue_localization.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

        <div class="figure-card">
          <img src="figures/fig5_physiological_metabolic_bridge.png" alt="Figure 5: Multi-Omics Triangulation Links Hypobaric Vapor Diffusivity to Stomatal Closure, Oxylipins, and Glucosinolates" onclick="openModal(this.src, 'Figure 5 | Multi-Omics Triangulation Links Hypobaric Vapor Diffusivity to Stomatal Closure, Oxylipins, and Glucosinolates')">
          <div class="figure-body">
            <div class="figure-title">Figure 5: Physiology & LC-MS Metabolomics</div>
            <div class="figure-caption">Ecotron stomatal gas exchange and chlorophyll fluorescence kinetics at 62 kPa, LC-MS galactolipid and glucosinolate profiling, and 70% RH metabolic rescue.</div>
            <div class="figure-footer">
              <a href="figures/fig5_physiological_metabolic_bridge.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

        <div class="figure-card">
          <img src="figures/fig6_nasa_exploration_atmosphere_counterfactual.png" alt="Figure 6: In-Silico Counterfactual Prediction of Arabidopsis Response to NASA's Exploration Atmosphere" onclick="openModal(this.src, 'Figure 6 | In-Silico Counterfactual Prediction of Arabidopsis Response to NASA Exploration Atmosphere')">
          <div class="figure-body">
            <div class="figure-title">Figure 6: Counterfactual Synthesis & LOCO</div>
            <div class="figure-caption">Leave-One-Condition-Out validation across held-out regimes, TabPFN v2 counterfactual pathway trajectories under NASA setpoints, and hub gene barosensory persistence.</div>
            <div class="figure-footer">
              <a href="figures/fig6_nasa_exploration_atmosphere_counterfactual.png" target="_blank">View PNG (300 DPI)</a>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- Jupyter Notebooks -->
    <section id="notebooks">
      <h2 class="section-heading">📓 Executable Jupyter Notebooks</h2>
      <p>All five research workpackages are provided as fully executed, reproducible Jupyter notebooks containing code, documentation, statistical tests, and inline figures:</p>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Notebook</th>
              <th>Workpackage Topic</th>
              <th>Key Models & Analyses</th>
              <th>Outputs</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>01_data_harmonization.ipynb</strong></td>
              <td>Forensics & Deduplication</td>
              <td>TabPFN v2 Organ Classifier, CEL Header Audit</td>
              <td>Figure 1, Table S1</td>
            </tr>
            <tr>
              <td><strong>02_tabpfn_decoupling.ipynb</strong></td>
              <td>Atmospheric Decoupling & Hubs</td>
              <td>TabPFN v2 (PHE) Regression, Multivariable Orthogonal Hubs, SHAP</td>
              <td>Figures 2 & 3, Tables S2A–S3</td>
            </tr>
            <tr>
              <td><strong>03_cellular_mapping.ipynb</strong></td>
              <td>Cellular & Single-Nucleus Atlas</td>
              <td>TRAP-seq Translatome, 40,860 Root Single Nuclei (GSE308672)</td>
              <td>Figure 4, Tables S4A–B</td>
            </tr>
            <tr>
              <td><strong>04_phenotypic_bridge.ipynb</strong></td>
              <td>Physiology & Metabolomics</td>
              <td>Ecotron Gas Exchange, LC-MS Oxylipins, SnRK1 Proteomics</td>
              <td>Figure 5, Tables S5A–C</td>
            </tr>
            <tr>
              <td><strong>05_counterfactual_synthesis.ipynb</strong></td>
              <td>NASA Setpoints & Humidity Rescue</td>
              <td>LOCO Validation, Counterfactual Simulator, 70% RH Rescue</td>
              <td>Figure 6, Tables S6A–B</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Data & Tables Download -->
    <section id="downloads">
      <h2 class="section-heading">📥 Supplementary Data Tables (CSV)</h2>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Table ID</th>
              <th>Description</th>
              <th>Dimensions</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Table S1</strong></td>
              <td>Harmonized 130 Hypobaric Microarrays Forensic Audit</td>
              <td>130 rows × 28 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S1_Harmonized_130_Hypobaric_Arrays_Forensic_Audit.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S2A</strong></td>
              <td>Multi-Task Physical Regression Benchmarks (95% Bootstrap CI)</td>
              <td>18 rows × 12 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S2A_Regression_Benchmarks_Bootstrap95CI.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S2B</strong></td>
              <td>4-Class Atmospheric Regime Classification Benchmarks</td>
              <td>7 rows × 11 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S2B_Classification_Benchmarks_Bootstrap95CI.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S2C</strong></td>
              <td>Slice-Based Error Analysis Across Biological Subgroups</td>
              <td>30 rows × 8 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S2C_Slice_Based_Error_Analysis.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S3</strong></td>
              <td>Exploration Atmosphere Molecular Hub Nodes (22,746 Probesets)</td>
              <td>22,746 rows × 18 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S3_Exploration_Atmosphere_Molecular_Hub_Nodes.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S4A</strong></td>
              <td>Cell-Type TRAP-seq and Single-Nucleus Lineage Atlas</td>
              <td>12 pathways × 24 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S4A_Pathway_CellType_TRAP_and_SingleNucleus_Atlas.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S4B</strong></td>
              <td>Top-80 Atmospheric Hubs Cell-Type & Single-Nucleus Localization</td>
              <td>80 rows × 26 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S4B_Top80_Hubs_CellType_and_SingleNucleus_Localization.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S5A</strong></td>
              <td>Zenodo 16536514 Physiological Gas Exchange Stats (62 kPa vs 101 kPa)</td>
              <td>12 traits × 11 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S5A_Zenodo16536514_Physiology_62kPa_vs_101kPa_Stats.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S5B</strong></td>
              <td>Zenodo 16536514 Pressure × Humidity Factorial Metabolomics</td>
              <td>14 compounds × 14 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S5B_Zenodo16536514_Metabolomics_Pressure_x_Humidity_Triangulation.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S5C</strong></td>
              <td>PXD002353 SnRK1.1 Phosphoproteome & Transcriptome Integration</td>
              <td>5,454 proteins × 12 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S5C_PXD002353_SnRK1_Proteome_Transcriptome_Integration.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S6A</strong></td>
              <td>NASA Exploration Atmosphere Counterfactual Predictions</td>
              <td>6 setpoints × 42 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S6A_NASA_Exploration_Atmosphere_Counterfactual_Predictions.csv" target="_blank">CSV</a></td>
            </tr>
            <tr>
              <td><strong>Table S6B</strong></td>
              <td>Leave-One-Condition-Out (LOCO) Model Generalization Benchmark</td>
              <td>20 rows × 8 cols</td>
              <td><a href="https://raw.githubusercontent.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn/main/arabidopsis_exploration_atmosphere/manuscript/tables/Table_S6B_Leave_One_Condition_Out_Validation.csv" target="_blank">CSV</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Citation & Open Science -->
    <section id="citation">
      <h2 class="section-heading">📚 Citation & Open Science</h2>
      <p>If you use this compendium, TabPFN v2 model pipelines, or counterfactual predictions in your research, please cite:</p>
      <pre style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #1e293b;">@article{BLiSS_Exploration_Atmosphere_2026,
  title   = {Decoupling Total Barometric Pressure from Oxygen Partial Pressure in the Arabidopsis thaliana Spaceflight Exploration Atmosphere Using the TabPFN v2 Tabular Foundation Model},
  author  = {BLiSS Multi-Omics Consortium and Space Plant Biology Working Group and Barker, Richard},
  journal = {Nature Plants (Submitted)},
  year    = {2026},
  url     = {https://github.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn}
}</pre>
    </section>

  </main>

  <!-- Modal Lightbox for Image Zoom -->
  <div id="imageModal" class="modal" onclick="closeModal()">
    <span class="modal-close" onclick="closeModal()">&times;</span>
    <img class="modal-content" id="modalImg">
    <div class="modal-caption" id="modalCaption"></div>
  </div>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="footer-content">
      <div class="footer-col">
        <h4>About the Project</h4>
        <p>
          Conducted within the Collaborative Science Environment (CoSE Cloud) in partnership with NASA Open Science Data Repository (OSDR), GeneLab, and international space biology researchers.
        </p>
      </div>
      <div class="footer-col">
        <h4>Open Science Repositories</h4>
        <p>
          Data sourced from GEO (GSE87867, GSE87868/OSD-136, GSE87903, GSE87904, GSE14493, GSE14502, GSE308672), Zenodo (16536514), and PRIDE (PXD002353).
        </p>
      </div>
      <div class="footer-col">
        <h4>Links & Contact</h4>
        <p>
          GitHub: <a href="https://github.com/dr-richard-barker/arabidopsis-exploration-atmosphere-tabpfn" target="_blank">arabidopsis-exploration-atmosphere-tabpfn</a><br>
          License: MIT Open Source<br>
          CoSE AstroBotany & Deep Space Agriculture
        </p>
      </div>
    </div>
  </footer>

  <script>
    function openModal(src, caption) {
      const modal = document.getElementById("imageModal");
      const img = document.getElementById("modalImg");
      const cap = document.getElementById("modalCaption");
      modal.style.display = "block";
      img.src = src;
      cap.innerText = caption;
    }
    function closeModal() {
      document.getElementById("imageModal").style.display = "none";
    }
    document.addEventListener("keydown", function(e) {
      if (e.key === "Escape") closeModal();
    });
  </script>

</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html_content)
    print(f"Generated {DOCS_DIR / 'index.html'}")


def generate_jekyll_config():
    config_content = """# Jekyll configuration for GitHub Pages
title: Arabidopsis Exploration Atmosphere TabPFN
description: Decoupling Total Barometric Pressure from Oxygen Partial Pressure in Arabidopsis using TabPFN v2
theme: jekyll-theme-cayman
plugins:
  - jekyll-seo-tag
"""
    (DOCS_DIR / "_config.yml").write_text(config_content)
    print(f"Generated {DOCS_DIR / '_config.yml'}")


def generate_github_workflow():
    workflow_content = """name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'arabidopsis_exploration_atmosphere/docs'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
    wf_path = PROJECT_DIR.parent / ".github" / "workflows" / "deploy-pages.yml"
    wf_path.parent.mkdir(parents=True, exist_ok=True)
    wf_path.write_text(workflow_content)
    # Also write inside arabidopsis_exploration_atmosphere
    (PROJECT_DIR / ".github" / "workflows" / "deploy-pages.yml").parent.mkdir(parents=True, exist_ok=True)
    (PROJECT_DIR / ".github" / "workflows" / "deploy-pages.yml").write_text(workflow_content)
    print(f"Generated {wf_path}")


def main():
    generate_css()
    generate_index_html()
    generate_jekyll_config()
    generate_github_workflow()
    print("\n=== GITHUB PAGES AND WORKFLOW BUILT SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
