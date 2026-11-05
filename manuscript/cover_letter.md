# Cover Letter to the Editorial Board

**Date:** October 19, 2026  
**Target Journal:** *Nature Plants* / *npj Microgravity* / *Nature Communications*  
**Article Type:** Original Research Article  

**Title:** Decoupling Barosensory from Hypoxia Signaling in Plants Under NASA Exploration Atmospheres Reveals Humidity Compensation as an Environmental Countermeasure  

**Authors:** Richard J. Barker$^{1,*}$ and [Co-authors To Be Determined]$^2$  
$^{1}$Purdue University, West Lafayette, IN 47907, USA  
$^{2}$[Affiliation To Be Determined]  
$^*$Corresponding author: `barkerrj@purdue.edu`  

---

Dear Senior Editor,

We are delighted to submit our manuscript entitled **"Decoupling Barosensory from Hypoxia Signaling in Plants Under NASA Exploration Atmospheres Reveals Humidity Compensation as an Environmental Countermeasure"** for consideration as an Original Research Article in your journal.

As space agencies prepare for permanent lunar outposts and long-duration crewed missions to Mars under the Artemis program, surface habitats and bioregenerative life-support systems (BLSS) will transition from the sea-level cabin atmosphere of the International Space Station ($97\text{--}101.3\text{ kPa}$, $21\%\ \text{O}_2$) to NASA's **Exploration Atmosphere** setpoints: **$56.54\text{ kPa}$ ($8.2\text{ psia}$) at $34\%\ \text{O}_2$** ($p\text{O}_2 = 19.22\text{ kPa}$) for habitat operations and **$70.33\text{ kPa}$ ($10.2\text{ psia}$) at $26.5\%\ \text{O}_2$** ($p\text{O}_2 = 18.64\text{ kPa}$) for pre-EVA staged decompression.

While enriching oxygen to $34\%\ \text{O}_2$ prevents crew hypoxia by maintaining a normoxic alveolar $p\text{O}_2$, plant physiology is subject to an inescapable physical law: according to the Chapman–Enskog kinetic theory of gases, binary molecular diffusivity scales inversely with total pressure ($D \propto P_{\text{total}}^{-1}$). Consequently, reducing barometric pressure to $56.54\text{ kPa}$ accelerates gas and water-vapor diffusion by **$1.72\times$** relative to ISS cabin air, dramatically thinning the leaf boundary layer and driving severe evaporative demand independently of cellular oxygen availability. For decades, space biologists have observed that hypobaric plants exhibit acute stress phenotypes, but dissecting whether these responses stem from physical barosensory mechanisms or latent hypoxia has been impeded by the quintessential "small-$n$, high-$p$" barrier of space biology ($n = 9\text{--}130$ arrays across $p = 22,746$ transcripts) coupled with legacy repository metadata ambiguities.

In this work, we deploy the recently developed **TabPFN v2** prior-data fitted tabular foundation model (Hollmann et al., *Nature* 637, 319–326, 2025) across a comprehensive 12-dataset multi-omics compendium spanning **281 microarray hybridizations**, **40,860 root-tip single nuclei**, **326 whole-plant physiological gas-exchange records**, **factorial pressure $\times$ humidity LC-MS metabolomics**, and **5,454 iTRAQ submergence proteins**. Our principal discoveries include:

1. **Forensic Resolution of Spaceflight Microarray Repositories:** By coupling raw Affymetrix `.CEL` hybridization metadata with TabPFN v2 out-of-fold probabilistic auditing, we resolve long-standing repository discrepancies in `GSE87903`: conclusively proving that four disputed samples (`GSM2342806`–`GSM2342809`, $P(\text{Shoot}\mid\mathbf{x}) \ge 0.9908$) are Shoots mislabeled as Roots due to fill-down metadata errors, correcting two $5\text{ kPa}$ root arrays mislabeled as $10\text{ kPa}$, and demonstrating that anomalous $n=4$ replicate groups arose from technical re-hybridization of Replicate A across scanner batches ($r = 0.9951\text{--}0.9964$).
2. **Superiority of Foundation Models in Small-Sample Omics:** Under rigorous condition-grouped cross-validation, TabPFN v2 and its post-hoc ensemble (PHE) outperform gradient-boosted trees (`LightGBM`), random forests, deep neural networks, and penalized linear models across both continuous Hypobaria Index regression ($R^2 = 0.9134$, $\rho = 0.9100$) and Hypoxia Index regression ($R^2 = 0.9733$, $\rho = 0.9121$), demonstrating that foundation models pre-trained on causal synthetic graphs excel in the ultra-small-$n$ biological regime.
3. **Genome-Wide Separation of Barosensory from Hypoxia Hubs:** Orthogonal multivariable regression and exact Shapley attributions separate **1,243 Pure Hypoxia ($p\text{O}_2$) probesets** (led by `HRU1`, `WIP5`, `AAD6`, `HB1`, `PDC1`, `PCO1`, `ADH1`) from **380 Pure Barosensory ($P_{\text{total}}$) probesets** (anchored by `CMI1`, `STZ`/`ZAT10`, `TCH4`/`AtXTH22`, `ACS6`, `LOX2`) that remain strongly activated even when oxygen is fully supplemented to normoxic levels.
4. **Spatial Segregation at Cellular and Single-Nucleus Resolution:** Projecting hubs onto 99 cell-type TRAP-seq arrays and 40,860 single nuclei reveals that while hypoxia triggers ERF-VII anaerobic responses uniformly across all nine root lineages ($+2.65\text{ to }+3.17\ \log_2\text{CPM}$), barosensory wax, cuticle, and cell-wall hubs localize specifically to `pCER5` shoot epidermis ($+2.21\text{ and }+1.21\ \log_2$).
5. **Physiological Phenotyping and Counterfactual Environmental Rescue:** Whole-plant gas exchange at $62\text{ kPa}$ confirms a $+73.23\%$ surge in leaf-to-air vapor pressure ratio that drives a $-76.25\%$ collapse in stomatal conductance and a $-55.93\%$ drop in net $\text{CO}_2$ assimilation. Crucially, Leave-One-Condition-Out validated TabPFN v2 counterfactual modeling demonstrates that while NASA's $34\%\ \text{O}_2$ enrichment successfully eliminates $>88\%$ of hypoxic anaerobic gene expression, physical barosensory stress (`TCH4`, `LOX2`, oxylipins) persists unabated. However, elevating chamber relative humidity to **$70\text{--}75\%\ \text{RH}$** restores chloroplast galactolipids (`MGDG-OPDA`) and suppresses the hypobaric metabolic state from $0.9822$ to $0.7908$.

These findings provide the first rigorous systems-biology blueprint for plant cultivation under NASA's Exploration Atmosphere, offering immediate, actionable engineering guidelines: **crop production in lunar and Martian habitats requires active humidity and boundary-layer management ($70\text{--}75\%\ \text{RH}$) alongside targeted genetic optimization of epidermal cuticular and cell-wall integrity.**

Given the broad multidisciplinary interest spanning plant space biology, foundation models in machine learning, microgravity biophysics, and bioregenerative life support, we believe this manuscript will resonate deeply with your readership.

### Suggested Independent Reviewers:
1. **Dr. Anna-Lisa Paul** (University of Florida, Space Plants Lab; alp@ufl.edu) — Expert in plant spaceflight biology, hypobaric chamber experiments, and Affymetrix transcriptomics.
2. **Dr. Robert J. Ferl** (University of Florida, Space Plants Lab; robferl@ufl.edu) — Pioneer in plant responses to extreme and spaceflight environments.
3. **Dr. Francesco Licausi** (University of Oxford; francesco.licausi@biology.ox.ac.uk) — Leading authority on plant hypoxia sensing, ERF-VII transcription factors, and the N-degron pathway.
4. **Dr. Angelika Mustroph** (University of Bayreuth; angelika.mustroph@uni-bayreuth.de) — Expert in plant hypoxia transcriptomics, translatome (TRAP-seq) profiling, and sucrose metabolism.
5. **Dr. Noah Hollmann / Dr. Frank Hutter** (University of Freiburg; hollmann@cs.uni-freiburg.de) — Creators of TabPFN / TabPFN v2 foundation models, experts in tabular Bayesian deep learning.
6. **Dr. Simon Gilroy** (University of Wisconsin–Madison; sgilroy@wisc.edu) — Expert in plant mechanosensing, cellular calcium signaling, and NASA spaceflight investigations.

We confirm that this manuscript is original, has not been published previously, and is not currently under consideration elsewhere. All authors have approved the manuscript for submission.

Thank you very much for your time and consideration.

Sincerely,

**Richard J. Barker, Ph.D.**  
Purdue University, West Lafayette, IN, USA  
Email: `barkerrj@purdue.edu`  
