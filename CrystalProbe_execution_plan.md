# CrystalProbe

**A 9-month execution plan for an interpretability-first foundation in trustworthy polymorph prediction.**

*Sister project to PsychProbe; a credible first step toward POLARIS.*

---

## Document purpose

This is the operating plan for the team that will build CrystalProbe over the next nine months. It defines the four deliverables, who owns what, how the work is sequenced, what it costs, where it gets published, what could go wrong, and what the world looks like at month 9 if we succeed.

It is deliberately scoped down from POLARIS. POLARIS is the eight-module empire we would build with a real budget and a real team. CrystalProbe is what three part-time researchers can credibly ship in nine months — and, importantly, what the field actually needs first regardless of who builds the rest.

The throughline is: **if polymorph prediction is going to influence pharmaceutical decisions, we have to know when to trust the predictions before we make more of them.** That is the safety contribution. Every deliverable in this plan exists to serve that goal.

---

## 1. The thesis

Three foundation MLIPs (MACE-OFF, AIMNet2, UMA) have hit the accuracy threshold for organic polymorph ranking in 2024–2025. The community is now layering production pipelines on top of them — FastCSP from Meta, Lavo-NN from Lavo Life Sciences, Schrödinger's commercial CSP module. These pipelines are being adopted, cited, and deployed in pharma decisions. None of them ships with calibrated uncertainty. Almost none of them characterises *where the underlying MLIPs systematically fail*. A pharma scientist running FastCSP today gets a polymorph ranking and a number; they do not get an honest answer to "should I trust this number for *this* molecule?"

That gap is where CrystalProbe lives. We build:

1. **A polymorph-pair benchmark** — a curated, openly redistributable set of crystal-structure pairs with verified experimental relative stability, designed specifically for diagnosing where MLIPs succeed and fail.
2. **A behavioural fingerprint of the major MLIPs** — using the benchmark, characterise MACE-OFF, AIMNet2, and UMA on systematic chemistry slices, and publish the results.
3. **An uncertainty-aware MLIP wrapper** — a small, well-tested Python package that adds calibrated uncertainty and out-of-distribution detection to existing MLIPs, with the calibration grounded in the benchmark.
4. **A FastCSP usability layer** — defaults, documentation, and integration with the wrapper so that an academic-budget user can run honest CSP on a single A100.

These four pieces share a common insight: the way you make polymorph prediction *good* (in the medical sense) is to make every prediction self-aware. The pipelines exist; the trust infrastructure does not.

The work is also strategic in three ways:

- **It is publishable.** Each of the four deliverables maps to a paper or open-source artifact that the field will cite. None of them require winning a Blind Test or beating commercial software; they fill a gap.
- **It compounds.** The benchmark feeds the fingerprint paper, the fingerprint informs the wrapper, the wrapper enables the FastCSP layer. By month 9 they form a coherent stack.
- **It defers the hard organisational problems.** No CSD licensing crisis, no pharma partnership negotiations, no consortium governance. We use what is open (OMC25, CPOSS209, FastCSP, Genarris 3.0) and make it more trustworthy.

If the work lands, it is the credential and infrastructure for whatever comes next — POLARIS Phase 1, an academic partnership, a small commercial wedge, or all three. If parts of it falter, each deliverable is independently valuable and can be released on its own.

---

## 2. The four deliverables

### Deliverable 1 — The Polymorph-Pair Benchmark

**What it is.** A curated, openly redistributable dataset of polymorph pairs (same molecule, two crystal forms) where the experimental relative stability is well-established. Each pair includes both structures (CIF), the molecule's identity (SMILES, InChI), the experimental stability ordering, and the conditions under which that ordering holds.

**Target scale.** v0.5: 50 pairs across 25 molecules. v1.0: 200–300 pairs across 60–100 molecules.

**Sources.**
- CPOSS209 (open, redistributable). 209 structures across 20 small pharmaceutical molecules — yields roughly 190 within-molecule pairs. This is the spine of the benchmark.
- 7th CCDC Blind Test database (171,679 entries; mixed redistribution rights — needs careful filtering).
- Polymorphs reported in open-access publications with deposited CIFs that authors have explicitly released under permissive licences.
- A small POLARIS-curated set: pairs we construct from OMC25 entries by matching to experimentally-known polymorphs.

**What gets annotated per pair.** Identity metadata (SMILES, InChI, common name, CAS); structural metadata (space group, Z′, density, lattice parameters); experimental stability data (which form is stable, at what temperature, under what conditions, with citation); chemistry classification (functional groups, H-bond motifs, conformational flexibility class, rigid/flexible label); known difficulties (disorder presence, multiple conformers, etc.). All of this in a clean Pydantic schema, version-controlled, with a JSON Lines manifest.

**What "Done" looks like.**
- Versioned dataset on Zenodo with DOI.
- HuggingFace Datasets mirror for easy programmatic access.
- A peer-reviewed Data Descriptor (npj's *Scientific Data* or equivalent) describing the construction methodology and rationale.
- A Python package (`crystalprobe.benchmark`) that loads, slices, and iterates the dataset.
- Explicit licensing: CC-BY 4.0 for redistributable subsets, with clear separation from any subsets that have inherited restrictions.

**Owner.** Yuliana, with Joan supporting on schema design.

**Why Yuliana.** This is a sustained, careful curation task that requires reading polymorph papers and extracting structured data from them. It is exactly the documentalist/psychologist's strength — the same kind of work that produced the PsychProbe behavioural feature vector. It is not a software engineering task and should not be one.

**Risks.**
- Curation takes longer than expected (it always does). Mitigation: target v0.5 at month 2, accept that v1.0 may slip to month 5.
- Some pairs have ambiguous experimental stability (two studies disagree). Mitigation: explicit "ambiguous" tag, document the disagreement, exclude from primary metrics but include as a research-interest subset.
- Reviewers may want CSD-derived pairs for breadth. Mitigation: have at least one collaborator with CSD access (the Day group at Southampton or the Marom group at CMU is the natural ask) for confirmatory cross-validation; do not depend on it for the primary release.

### Deliverable 2 — The Behavioural Fingerprint Paper

**What it is.** A peer-reviewed paper that takes the benchmark and uses it to characterise the systematic behaviour of the major open-source MLIPs. Modelled directly on PsychProbe methodology: structured probes, behavioural feature decomposition, failure-mode catalog.

**Models evaluated.** MACE-OFF (medium and large checkpoints), AIMNet2, UMA (small and medium checkpoints), MACE-OMOL if available; classical force fields (OPLS3, GAFF) as a sanity baseline. Possibly Lavo-NN if Lavo releases an inference API in time.

**Metrics computed per model.**
- *Ranking accuracy*: probability the MLIP correctly identifies the more stable form across each pair. Stratified by chemistry class.
- *Energy gap accuracy*: signed and unsigned error in the predicted stability gap, vs. experimental free energy difference where known.
- *Force RMSE on relaxed structures*: how well the model represents local geometry.
- *Conformational sensitivity*: how the prediction changes under small input perturbations (temperature, slight cell scaling).
- *Out-of-distribution behaviour*: error growth as a function of distance from the training distribution.

**Slices we report on.**
- Functional groups (carboxylic acids, amides, halogens, sulfur-containing rings).
- H-bond motif type (single donor-acceptor, charge-assisted, halogen bonds).
- Conformational flexibility (rigid, semi-rigid, flexible).
- Z′ (Z′=1 vs. Z′>1).
- Disorder presence (ordered vs. flagged-disordered).

**The narrative.** The paper's claim is *not* "we beat the SOTA." It is "we characterised the SOTA's behavioural surface, and here is where it can and cannot be trusted, and here is the methodology by which others can extend this analysis to future MLIPs." This matters because it tells a pharma user: "for your halogenated molecule, MACE-OFF is reliable; for your zwitterionic salt, switch to AIMNet2 or wait for MACE-POLAR-1."

**What "Done" looks like.**
- ChemRxiv preprint by month 6.
- Submission to *npj Computational Materials* or *Chemical Science* by month 7.
- All analysis code reproducible from the package; all figures regenerable.

**Owner.** Joan, with the ML researcher on inference infrastructure.

**Why Joan.** This is the central scientific artifact and aligns with Joan's interpretability research stack. It is also where the team's unique angle is most differentiating from existing CSP groups.

**Risks.**
- The findings are uninteresting (all models behave similarly). Mitigation: even null results are publishable in this space, and the methodology contribution stands. But also — this is unlikely given the heterogeneity of training data across the three model families.
- A foundation model releases a new checkpoint mid-project. Mitigation: pin versions for the headline analysis; treat new checkpoints as a future-work appendix.
- We discover something unflattering about a model whose authors are well-connected. Mitigation: ferocious empirical rigor, multiple statistical tests, share findings with model authors before publication for technical correctness review (not approval). We are scientists, not diplomats; honest findings matter more than friction.

### Deliverable 3 — The Uncertainty-Aware MLIP Wrapper

**What it is.** A small, well-tested Python package that wraps MACE-OFF and AIMNet2 (and trivially extends to UMA) with calibrated uncertainty and out-of-distribution detection. Provides one canonical API: `wrapped_model.predict(structure)` returns `(energy, energy_uncertainty, forces, force_uncertainty, ood_flag)`.

**Uncertainty sources.**
- *Deep ensemble*: run K different model checkpoints (different sizes, different training seeds) and report ensemble variance.
- *Distance-based OOD*: embed the structure in MLIP feature space, compute distance to nearest training-set structure, return as OOD score.
- *Conformational sensitivity*: small noise perturbations to atomic positions, report propagation of variance.

We will *not* implement Bayesian neural networks or evidential regression in v1. Both are research-grade techniques whose ROI is unclear and whose calibration is genuinely difficult. Deep ensembles + OOD detection give 80% of the value at 20% of the engineering cost.

**Calibration.** Every uncertainty estimate is calibrated against the polymorph-pair benchmark from Deliverable 1. Reliability diagrams and Brier scores are part of the package's test suite. A key claim of the package: "if we say the energy uncertainty is X, then with frequency Y the true energy lies within X."

**What "Done" looks like.**
- Public GitHub repository (Apache 2.0 license).
- PyPI package (`pip install crystalprobe-uncertainty`).
- Comprehensive test suite (>80% coverage, all calibration claims verified on the benchmark).
- Documentation site with worked examples.
- A short software paper in the *Journal of Open Source Software* (JOSS).

**Owner.** ML researcher, with Joan integrating into the fingerprint paper analysis.

**Risks.**
- Deep ensembles for MACE-OFF/AIMNet2 may give miscalibrated uncertainties out of the box. Mitigation: temperature scaling and isotonic regression as post-hoc calibration steps. This is well-trodden territory.
- The OOD detector is fooled by structurally similar but chemically novel molecules. Mitigation: be honest about its scope in the documentation; report failure cases.
- Computational cost of an ensemble may be too high for routine use. Mitigation: provide both a "fast" mode (single model + perturbation-based uncertainty) and a "full" mode (K-model ensemble).

### Deliverable 4 — The FastCSP Usability Layer

**What it is.** Either a fork of FastCSP or, preferably, an upstream contribution, that adds:
- Sensible defaults for hardware tiers (laptop / single A100 / multi-GPU).
- The CrystalProbe uncertainty wrapper, applied to every ranking prediction.
- A polymorph-pair regression test running against the benchmark on every commit.
- Clear documentation written for academic-budget users, not Meta engineers.
- Honest reporting: every output names the MLIP version, the uncertainty estimate, the OOD status, the runtime, and the cost.

**Strategy.** Contribute upstream first. FastCSP is an Apache-2.0 project at `github.com/facebookresearch/fairchem` and the authors have explicitly noted limitations around flexible molecules and Z′ > 1. We submit pull requests (with thorough tests) for the uncertainty integration and the documentation. If those land, we are a known contributor and we have institutional credibility. Only fork if upstream contribution is rejected or unreasonably delayed.

**Why this matters.** FastCSP is *the* open-source CSP pipeline of the 2025–2026 wave. By being a known and trusted contributor, we ride its visibility instead of fighting it. The "make it good" goal is served by making the most-used tool more trustworthy, not by building our own competing tool nobody adopts.

**What "Done" looks like.**
- At least three meaningful PRs merged into upstream FastCSP.
- A README and walkthrough showing CrystalProbe + FastCSP for a complete polymorph analysis on one molecule, runnable from a fresh `pip install` in under an hour on a rented A100.
- Optional: if upstream is slow, a `fastcsp-academic` fork that bundles the usability layer.

**Owner.** ML researcher and Joan, jointly.

**Risks.**
- Meta's team may not accept all contributions. Mitigation: small PRs, good tests, friendly tone; fork only as a last resort.
- The pace of FastCSP development outstrips ours and we are constantly chasing. Mitigation: pin to a stable release; only re-base when CrystalProbe v1.0 is shipping.
- FastCSP changes its licensing or API. Low probability but mitigation: document our modifications as a separate package that depends on FastCSP rather than modifying it in place.

---

## 3. Team and operational model

**Joan (project lead, principal researcher).** Owns the fingerprint paper (Deliverable 2) and the overall scientific direction. Reviews everything. Estimated availability: 15–25 hours/week, fluctuating with consulting work.

**ML researcher (engineering lead).** Owns the uncertainty wrapper (Deliverable 3) and shares the FastCSP integration (Deliverable 4). Estimated availability: depends on their other commitments — needs explicit conversation.

**Yuliana (curation and documentation lead).** Owns the benchmark dataset (Deliverable 1) and contributes to the fingerprint paper as a co-author. Estimated availability: needs explicit conversation; the dataset is sustained work.

**Operating rhythm.**
- Weekly 60-minute team sync. Standing agenda: progress per deliverable, blockers, decisions needed, compute spend.
- Monthly review with explicit go/no-go evaluation against milestones.
- Quarterly external check-in with at least one external collaborator (we will identify one in Month 1 — see Section 5).
- All work in a single GitHub organisation. All compute experiments tracked in a shared notebook (one of: Weights & Biases free tier, Aim, or just a structured Markdown log — we choose in Week 1).

**Critical conversations to have in Week 1.**
- Confirm hours/week each person can realistically commit. The plan is calibrated to roughly 80 person-hours/week total. If actual capacity is lower, the plan flexes — likely by descoping the FastCSP layer (Deliverable 4) first.
- Confirm everyone is comfortable with the publishing strategy (open-access, ChemRxiv preprints, Apache/CC-BY licenses).
- Confirm authorship policy upfront. Joan first-author on Deliverable 2 paper. Yuliana first-author on Deliverable 1 data descriptor. ML researcher first-author on Deliverable 3 software paper. Joint authorship across all three on each.

**Where we ask for outside help.**
- A senior CSP collaborator for the fingerprint paper. The natural asks, in priority order: Noa Marom (CMU), Graeme Day (Southampton), Matteo Salvalaglio (UCL). The pitch: "we are doing systematic interpretability work on MLIPs for organic crystal ranking; we would value senior input and possibly co-authorship; here is the v0.5 benchmark and our preliminary findings on aspirin and paracetamol." Send this in Month 3, when we have something concrete to show.
- A pharma reviewer for the methodology before submission. Less critical; can be sourced through ChemRxiv comments.

---

## 4. Timeline with decision gates

The work is structured as three quarters of three months each, with explicit decision gates between them.

### Quarter 1 (Months 1–3): Foundation

**Month 1 deliverables:**
- Repository structure set up. CI running. License chosen and committed.
- Benchmark schema (Pydantic) defined and reviewed by all three team members.
- v0.1 benchmark: 20 pairs across 10 molecules (the canonical demonstration set: aspirin, paracetamol, urea, glycine, naphthalene, ROY, mannitol, tolfenamic acid, carbamazepine, sulfathiazole). Loaded from CPOSS209.
- MACE-OFF and AIMNet2 inference infrastructure working on the 4060 Ti.
- A single end-to-end smoke test: run MACE-OFF on the 20-pair v0.1 benchmark, produce a ranking-accuracy number.

**Month 2 deliverables:**
- v0.5 benchmark: 50 pairs across 25 molecules.
- Initial fingerprint analysis on v0.5: ranking accuracy, energy gap accuracy, simple chemistry-class slicing.
- Uncertainty wrapper v0.1: deep ensemble of MACE-OFF medium + large, returning ensemble variance.
- First draft of fingerprint paper *outline* (not the paper itself, just the figure list and section structure).

**Month 3 deliverables:**
- v0.7 benchmark: 100 pairs, including initial 7th Blind Test entries we can include.
- Calibration analysis on v0.5/v0.7: are the uncertainty estimates well-calibrated? If not, what post-hoc fixes work?
- First external collaborator engaged (Marom, Day, or Salvalaglio).
- A 2,000-word ChemRxiv-style "preliminary findings" memo circulated to the external collaborator and 2–3 other trusted readers.

**Decision gate at end of Month 3:**

*Question: Is there a real signal in the fingerprint analysis?*

If yes (we see clear, reproducible behavioural differences between the MLIPs that map to chemistry classes): proceed to Q2 as planned.

If no (the models all behave roughly the same, or the noise dominates the signal): do a deliberate methodology pivot. The fingerprint paper becomes a methodology paper ("here is how to systematically benchmark MLIPs for polymorph ranking; here is the open benchmark; we apply it to three current models and find no significant differentiation, raising questions about training-data overlap"). This is *still publishable* and is *still valuable*, but it is a different paper. This gate exists to protect us from sunk-cost.

### Quarter 2 (Months 4–6): Build and write

**Month 4 deliverables:**
- v1.0 benchmark: 200+ pairs. Frozen for the headline analysis.
- Uncertainty wrapper v0.5: API stable, ensemble + OOD detection working, basic calibration.
- Fingerprint paper draft v1.0 (figures + intro + methods).
- FastCSP integration scoped (we read the FastCSP code carefully, identify our two or three target PRs).

**Month 5 deliverables:**
- v1.0 benchmark Data Descriptor draft (Yuliana first-author).
- Fingerprint paper draft v2.0 (results + discussion).
- Uncertainty wrapper v0.9: documentation, examples, test suite. Tagged release.
- First FastCSP PR submitted upstream.

**Month 6 deliverables:**
- ChemRxiv preprint of fingerprint paper.
- Uncertainty wrapper v1.0 on PyPI.
- v1.0 benchmark on Zenodo with DOI.
- Data Descriptor submitted to *Scientific Data* (or equivalent).

**Decision gate at end of Month 6:**

*Question: Did the preprint land well? (Defined as: at least one citation in another preprint within a month, or substantive Twitter/Bluesky engagement from at least three CSP researchers, or a serious email exchange with a relevant academic group.)*

If yes: proceed to Q3 with the FastCSP layer as planned. The credibility is real and the ecosystem effort is worth the time.

If no: descope. Q3 becomes consolidation — polish the wrapper, push the data descriptor through review, finish the fingerprint paper revision. Skip the FastCSP layer for now; it can be a follow-up project. There is no point integrating with a community that isn't paying attention to us.

### Quarter 3 (Months 7–9): Integrate, polish, position

**Month 7 deliverables (assuming Q3 proceeds as planned):**
- Two more FastCSP PRs submitted.
- Fingerprint paper revisions incorporated; submission to npj Computational Materials.
- Wrapper paper drafted for JOSS.

**Month 8 deliverables:**
- FastCSP layer documentation site live.
- Comprehensive integration walkthrough: "From SMILES to polymorph landscape with calibrated uncertainty in 60 minutes on one A100."
- Data Descriptor revised based on first-round reviews.
- Conference talk submission (CCDC user meeting, ACS Spring 2027, or MRS Fall 2026).

**Month 9 deliverables:**
- Public release of the integrated CrystalProbe stack.
- A blog post / Twitter thread / Bluesky thread synthesising what we built and why.
- A short white paper (~3,000 words) that summarises the project for funders and pharma readers.
- An honest retrospective: what worked, what didn't, what's next.

**End-state at Month 9.** The team has shipped: one peer-reviewed paper (in revision), one data descriptor (in revision), one PyPI package, one Zenodo dataset with DOI, three or more upstream PRs to FastCSP, and a coherent public story about why the work matters. We are credible. We are known. The path to POLARIS Phase 1 — or to a small commercial wedge, or to a serious academic partnership — is open.

---

## 5. Compute and budget

This is genuinely modest. The single largest line item is rented A100 spot time, and almost all of that is for benchmarking.

**Local compute (already owned).**
- Joan's RTX 4060 Ti (16GB VRAM). Sufficient for: MACE-OFF inference on small organic crystals, AIMNet2 inference, basic relaxation. Not sufficient for: UMA medium-checkpoint inference at scale, phonon calculations.

**Rented compute.**
- A100 80GB spot via Vast.ai or RunPod, ~$1–2/hour.
- Estimated total: 200–400 A100-hours across nine months.
- *Phase A (Months 1–3): UMA inference on benchmark.* ~50 hours.
- *Phase B (Months 4–6): Replicate analyses, ensemble runs, FastCSP experiments.* ~150 hours.
- *Phase C (Months 7–9): Integration runs, regression tests, final benchmarks.* ~150 hours.
- Total dollar estimate: $400–$800.

**API compute (LLM-mediated workflows).**
- OpenRouter: minor. Probably $20–$50 over nine months for occasional use of larger LLMs to draft documentation, summarise papers, or scaffold code.

**Hosting and infrastructure.**
- HuggingFace Datasets: free.
- Zenodo: free.
- GitHub: free for open source.
- PyPI: free.
- Documentation hosting (Read the Docs): free.

**Conference and travel.**
- Optional. One conference in late Q3 if a talk is accepted. Estimated $500–$1,500 if travel is required, $50 if virtual.

**APCs (article processing charges).**
- *npj Computational Materials*: open access, APC ~$2,500 in 2025.
- *Scientific Data* Data Descriptor: open access, APC ~$1,800.
- *JOSS*: free.
- *Chemical Science*: open access, APC ~$3,500.

**APC strategy.** The fingerprint paper is the only one where we would face a meaningful APC charge. Three options: (1) request fee waiver from the journal — Springer Nature has a waiver programme for authors from low- and middle-income countries, which covers Colombia; (2) submit to a venue that doesn't charge (Acta Cryst, Cryst Growth & Design via certain channels); (3) have the senior collaborator's institution cover the APC if they're a co-author. Option 1 is cleanest if we qualify.

**Total realistic budget across nine months:** $1,000 – $4,000 depending on whether APCs are waived and conference travel happens. This is genuinely affordable for an independent research effort.

**What we do if compute breaks.** The 4060 Ti can run all of Deliverable 3 and most of Deliverable 1 unaided. If A100 rental costs spike (or Joan's budget tightens), we can fall back to MACE-OFF only and produce a slightly narrower fingerprint paper. The plan is robust to compute disruption.

---

## 6. Publishing strategy

Three peer-reviewed outputs, plus public artifacts.

**Output 1: Behavioural fingerprint paper.**
- Preprint: ChemRxiv at end of Month 6.
- Submission: *npj Computational Materials* (preferred), with *Chemical Science* as backup.
- First author: Joan.
- Co-authors: ML researcher, Yuliana, plus (ideally) one external senior collaborator.
- Target word count: 6,000–8,000.

**Output 2: Benchmark Data Descriptor.**
- Submission: *Scientific Data* (Nature Portfolio).
- First author: Yuliana.
- Co-authors: Joan, ML researcher.
- Target word count: 4,000–5,000. These are short by design.

**Output 3: Software paper.**
- Submission: *Journal of Open Source Software* (JOSS).
- First author: ML researcher.
- Co-authors: Joan, Yuliana.
- Target word count: ~1,000. JOSS papers are deliberately short; the artifact is the package.

**Public artifacts (non-peer-reviewed).**
- Zenodo deposits of the dataset (DOI-citable).
- PyPI package for the wrapper.
- GitHub repositories for everything (Apache 2.0 license).
- A project website (minimal — a README with links is fine for v1).
- A month-9 retrospective blog post that synthesises the work for a non-specialist audience.

**On the question of arXiv vs. ChemRxiv.** ChemRxiv is the discipline-native preprint server, lower-friction for chemistry submissions, and does not require endorsement. Arxiv chem-ph requires endorsement, which is an extra step for an independent researcher — manageable but slower. Default to ChemRxiv for the chemistry preprint; cross-post to arXiv if endorsement is in place by month 6.

**On co-authorship with a senior CSP figure.** Strong recommended-yes for the fingerprint paper specifically. The senior collaborator's role is technical review and credibility transfer, not project direction. The asking-out conversation in Month 3 should be explicit: "we would value your review and possible co-authorship; we are not asking for funding or compute; here is what we have and where we are going."

**A note on style.** Materials science papers in 2025–2026 increasingly include a "limitations" or "negative findings" section. Embrace this. The fingerprint paper should explicitly enumerate the chemistry classes where our analysis is *not* informative, the assumptions baked into the calibration, and the open questions we did not resolve. This is both more honest and more strategically defensible — pre-empts reviewers and signals seriousness.

---

## 7. Risk register

Top eight risks, ranked by combined severity and probability.

**R1: Yuliana's available time is materially less than assumed (high probability).**
Curation is the bottleneck for everything. If Yuliana has fewer than ~10 hours/week, the v1.0 benchmark slips to Month 7, which slips the fingerprint paper to Month 10, which collapses Q3.
*Mitigation:* Have the explicit conversation in Week 1. If hours are limited, descope to v0.7 (100 pairs) for the headline analysis, and treat v1.0 as a post-publication expansion. Joan and the ML researcher absorb some curation tasks where feasible.

**R2: A foundation MLIP releases a major new version mid-project (medium probability).**
MACE-OFF v3, AIMNet3, UMA-2 — any of these would force re-runs.
*Mitigation:* Pin model versions explicitly in the benchmark and the wrapper. Treat new releases as "future work" sections in the paper. The contribution stands even if a newer model exists by publication time — in fact, that *strengthens* the methodology contribution.

**R3: The fingerprint analysis shows no interesting structure (low-medium probability).**
All models behave roughly equivalently; no useful chemistry-class differentiation.
*Mitigation:* Pivot to a methodology paper as described in the Q1 decision gate. The benchmark, the methodology, and the wrapper are all still valuable.

**R4: Senior collaborator declines (medium probability).**
The Marom/Day/Salvalaglio outreach gets no response or a polite no.
*Mitigation:* Approach in priority order; if all three decline, proceed without senior co-authorship. Reviewers may push back on the absence of pharma-domain credentials; respond by making the methodology contribution as airtight as possible.

**R5: FastCSP upstream contribution is slow or rejected (medium probability).**
PR review at large open-source projects is slow.
*Mitigation:* Submit small, well-tested PRs. Ship the standalone wrapper regardless. Fork as last resort with a clear fork-rationale document.

**R6: Reviewers demand CSD-licensed comparisons (medium probability).**
A reviewer says "your benchmark would be much stronger with the full CSD pharmaceutical pool" and rejects on that basis.
*Mitigation:* Pre-empt in the methods section: explicitly justify why open redistributability is a feature, not a bug, of the benchmark; provide CSD-derived spot-check confirmation through the senior collaborator's institutional access; reference the CCDC's own open releases (the 7th Blind Test database).

**R7: Joan's research bandwidth is consumed by other priorities (medium-high probability).**
Consulting work, PERSIST/PsychProbe deadlines, family commitments — all real.
*Mitigation:* Build the project to be resilient to one-month interruptions. The benchmark and wrapper progress can continue without Joan; only the fingerprint paper writing requires sustained Joan-attention. Plan for one such interruption in the timeline.

**R8: A competing group publishes a similar benchmark or fingerprint paper first (low probability).**
The space is small enough that this is unlikely but not impossible — Marom or Day could in principle produce something adjacent.
*Mitigation:* Move fast on the preprint. ChemRxiv timestamps establish priority. Even if a competing paper appears, our benchmark + methodology + open package together are differentiated; we are not just a paper, we are an infrastructure release.

**R9 (acknowledged but unmitigated): A pharma actor uses our predictions in a high-stakes decision and the prediction turns out to be wrong.**
This is a real ethical risk and not fully mitigable through technology alone.
*Position:* The wrapper, the documentation, and the paper all explicitly state: "research use only, not for regulatory or clinical decisions." Calibrated uncertainty + OOD flags reduce but do not eliminate the risk. We accept this residual risk as the cost of releasing a useful tool — the same trade-off every open-source CSP project makes — and document our position transparently.

---

## 8. What success looks like

By **Month 9**, we have:

1. A peer-reviewed paper in revision at *npj Computational Materials* characterising the systematic behaviour of MACE-OFF, AIMNet2, and UMA on a curated polymorph-pair benchmark, identifying chemistry classes where each model is reliable and each model fails. (Probably accepted by Month 12.)
2. A peer-reviewed Data Descriptor in revision at *Scientific Data* describing the benchmark itself.
3. A short JOSS paper accompanying the uncertainty wrapper.
4. A public benchmark on Zenodo (DOI-citable) and HuggingFace.
5. A public Python package on PyPI.
6. Three or more merged contributions to FastCSP upstream.
7. A working integration that runs from SMILES to a polymorph landscape with calibrated uncertainties on a single rented A100 in roughly an hour, for rigid drug-like molecules.
8. A working relationship with at least one senior CSP group.
9. A coherent public narrative: open-source, interpretability-first, safety-grounded.

**What this earns us.** Three concrete options for what comes next:
- Apply to NSF, EU, or Wellcome Trust for a grant to expand into POLARIS Phase 1, with the CrystalProbe stack as a credibility anchor.
- Negotiate a serious academic partnership with the senior collaborator for kinetics-aware or process-aware extensions.
- Build a small commercial offering: paid analysis service for academic and small-pharma users who can't afford Schrödinger or Lavo.

**What failure looks like (and why it's still okay).** The most likely failure mode is partial completion: we ship the benchmark and the wrapper, but the fingerprint paper drags into a Year 2 effort, and the FastCSP integration never quite happens. *That is still a win.* The benchmark and wrapper are independently citeable artifacts. The team has a real GitHub presence and a real paper in flight. The CrystalProbe brand exists. Year 2 starts with momentum, not from zero.

The failure mode we want to avoid is *wide-but-shallow*: starting all four deliverables, finishing none. The decision gates at Month 3 and Month 6 exist precisely to prevent this.

---

## 9. Week 1 tactical plan

Concrete to-do list for the first seven days. Most of this is the unglamorous foundation work that determines whether the next nine months are productive or chaotic.

**Day 1.** All-team kickoff call. Walk through this document. Have the hours-per-week conversation. Confirm authorship policy. Confirm tooling choices (GitHub org name, license choice, communication channel — Slack/Discord/Matrix, project board — GitHub Projects/Linear/just a Markdown file).

**Day 2–3 (Joan).** Set up the GitHub organisation. Create the four repositories: `crystalprobe-benchmark`, `crystalprobe-uncertainty`, `crystalprobe-fingerprint-paper`, `crystalprobe-fastcsp-layer`. Establish CI templates. Choose Apache 2.0 for code, CC-BY 4.0 for data. Write a one-page project README that states the mission and links to this document.

**Day 2–3 (Yuliana).** Read CPOSS209 paper and dataset structure. Sketch the benchmark schema in a Google Doc. Identify the 10 anchor molecules for v0.1.

**Day 2–3 (ML researcher).** Get MACE-OFF medium running on the 4060 Ti. Get AIMNet2 running. Confirm both can produce single-point energies for a sample organic crystal. Document any GPU memory constraints discovered.

**Day 4. Joint working session (3 hours).** Lock the benchmark schema. The schema is the contract — once it's set, Yuliana can curate independently and the ML researcher can build the loader independently. Use a Pydantic model with explicit examples.

**Day 5–6.** Each person executes against their first task. Yuliana: enter v0.1 anchor molecules into the schema. ML researcher: build the loader and the basic inference loop. Joan: write the literature review section of the fingerprint paper outline.

**Day 7.** First weekly sync. Honest assessment: did Week 1 land as planned? If not, what needs to change? Adjust the Month 1 milestone based on what we learned about real velocity.

**At the end of Week 1, we should have:**
- Repositories live, CI green, README in place.
- Schema agreed and committed.
- v0.1 benchmark started: 5–10 pairs in the canonical schema.
- One end-to-end run: load v0.1 → MACE-OFF inference → ranking accuracy number printed.

This last item is the *first integration test* of the whole project. Even a tiny end-to-end run confirms the architecture composes. Get this working in Week 1 and the rest of the project is engineering against a known shape. Skip it and the project is committed to a structure no one has tested.

---

## Appendix A — Benchmark schema sketch

A starting point for Day 4's working session. To be revised.

```python
from pydantic import BaseModel
from typing import Literal, Optional

class StructureRef(BaseModel):
    cif_path: str               # path to CIF file, relative to dataset root
    space_group: str            # e.g. "P21/c"
    z_prime: float              # Z′
    density_g_per_cm3: float
    source: Literal["CPOSS", "blind_test_7", "OMC25", "literature", "POLARIS_curated"]
    source_id: str              # original ID in source database
    license: Literal["CC-BY-4.0", "inherited_restricted"]

class ExperimentalEvidence(BaseModel):
    stability_ordering: Literal["A>B", "B>A", "A=B (within error)", "ambiguous"]
    temperature_K: Optional[float]
    relative_humidity: Optional[float]
    free_energy_diff_kJ_per_mol: Optional[float]
    free_energy_diff_uncertainty_kJ_per_mol: Optional[float]
    citation_doi: str
    notes: str

class ChemistryAnnotation(BaseModel):
    smiles: str
    inchi: str
    common_name: Optional[str]
    cas_number: Optional[str]
    flexibility_class: Literal["rigid", "semi_rigid", "flexible"]
    h_bond_motifs: list[str]    # e.g. ["amide", "carboxylic_acid"]
    has_halogen: bool
    has_charge: bool
    is_chiral: bool

class PolymorphPair(BaseModel):
    pair_id: str                # e.g. "ritonavir_form_I_vs_form_II"
    molecule: ChemistryAnnotation
    structure_a: StructureRef
    structure_b: StructureRef
    evidence: ExperimentalEvidence
    has_disorder: bool
    notes: str
    schema_version: str         # for forward compatibility
```

A v1.0 benchmark is a JSON Lines file of these records, plus the referenced CIFs in a structured directory.

---

*End of execution plan. Version 0.1. To be updated after the Week 1 kickoff and at each monthly review.*
