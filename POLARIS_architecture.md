# POLARIS

**Polymorph Open Landscape, AI Research, & Intelligence Suite**

*A next-generation open-source toolkit for predicting, ranking, and de-risking the polymorphism of organic crystals.*

---

## Document purpose

This is a build specification for the implementation team. It defines the vision, the system architecture, the eight modules of the suite, the cross-cutting infrastructure that binds them, the data and validation strategy, and a phased roadmap. It is opinionated where it needs to be and explicitly leaves open the questions that should not be settled before prototyping.

The document is structured so that each module section is a self-contained unit of work that a sub-team can own, with clearly defined inputs, outputs, dependencies, and validation criteria.

---

## 1. Vision

In June 1998, Abbott discovered that ritonavir — a life-saving HIV drug — was crystallising into a previously unseen, more stable, less soluble polymorph. The drug was rendered useless overnight. It took two years and hundreds of millions of dollars to recover, during which patients went without treatment.

The Ritonavir story is the field's founding wound. Twenty-seven years later, in December 2025, Iuzzolino et al. demonstrated retrospectively that current Crystal Structure Prediction (CSP) tools *would have* foreseen the disaster. And yet, by Marcus Neumann's accounting from over forty commercial CSP studies, between 15% and 45% of all small-molecule drugs currently on the market are sitting in metastable forms, kinetically trapped, with a more stable polymorph latent in their energy landscape. Each is a potential ritonavir.

The technical pieces to solve this are now in hand:

- **Foundation MLIPs** (MACE-OFF, AIMNet2, UMA, Lavo-NN) have collapsed the cost of energy ranking by one to two orders of magnitude.
- **OMC25** (Meta FAIR, 2025) released 27M molecular crystal DFT structures under CC-BY 4.0, ending the data drought for organic crystals.
- **The 7th CCDC Blind Test** (2024) established that hierarchical CSP combined with MLIPs achieves near-experimental accuracy on rigid drug-like molecules.
- **FastCSP**, **Genarris 3.0**, and **PyXtal** are open-source and good enough to serve as a substrate.

What does *not* yet exist is the integrated, kinetics-aware, process-aware, generative, multi-component, audit-trailed, computationally-graceful, mortal-friendly pipeline that turns these primitives into a public health asset.

POLARIS is that pipeline. The strategic ambition is to do for polymorphism what AlphaFold did for protein structure: take a fragmented technical field, integrate it into a usable open stack, validate it ferociously, and put it in the hands of every researcher who needs it.

---

## 2. Design principles

**Open-source first.** Every component is released under a permissive license (Apache 2.0 or MIT). Closed dependencies are isolated behind interfaces so they can be swapped. This is non-negotiable; it is what unlocks community contribution and breaks the current pharma duopoly of GRACE and Schrödinger.

**Modular, not monolithic.** Each module is a Python package with a well-defined public API and is independently testable. Modules communicate through serialisable data contracts (CIF for structures, Pydantic schemas for everything else). A research group should be able to take one module, replace it with their own, and contribute back without touching the rest.

**Foundation models as substrate, not implementation detail.** We do not train MLIPs from scratch. We wrap MACE-OFF, AIMNet2, and UMA, present them through a uniform interface, and treat their improvement as exogenous. This decouples our progress from the pace of foundation-model development.

**Honest uncertainty everywhere.** Every prediction returns a calibrated confidence interval. A polymorph energy of "−105.3 kJ/mol ± 1.2" is more honest and more useful than "−105.3". Uncertainty quantification is built into the contract, not bolted on.

**Computational graceful degradation.** The same workflow runs on (a) a single consumer GPU, (b) one A100 spot instance, (c) a small academic cluster, or (d) a national HPC system. The user gets the same answer at different speeds and confidence levels, never a "you cannot run this" error.

**Closed-loop with experiment.** Predictions can be queued for experimental validation through standardised interfaces to PXRD, automated screening platforms, and laboratory information systems. Experimental results flow back into the data layer and the foundation models retrain.

**Provenance by default.** Every output carries a hash of the model versions, datasets, and software used to produce it. Reproducibility is a first-class feature, not a research ethics afterthought.

**Polymorphism is more than thermodynamics.** Most current CSP answers the wrong question. The user does not want "which form has lowest free energy?", they want "which form will I get from ethanol at 5°C with 1.2× supersaturation?". The architecture commits to bridging structure prediction and process prediction.

---

## 3. System architecture

POLARIS is a layered system. Reading top to bottom, each layer depends only on the layers below it.

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │  CONDUCTOR — LLM agent layer (planning, routing, reporting)          │
 ├──────────────────────────────────────────────────────────────────────┤
 │  Eight modules:                                                      │
 │    KINETICA    DISARRAY    MULTIPLEX    HYDRA                        │
 │    GENESIS     PROCESS     OPENBENCH    INSIGHT                      │
 ├──────────────────────────────────────────────────────────────────────┤
 │  FOUNDRY — uniform MLIP / generative-model interface                 │
 ├──────────────────────────────────────────────────────────────────────┤
 │  DATAHUB — unified polymorph data layer                              │
 ├──────────────────────────────────────────────────────────────────────┤
 │  ANVIL — benchmarking & continuous validation                        │
 │  LAB BRIDGE — experimental interfaces (PXRD, robots, LIMS)           │
 │  LEDGER — provenance, hashing, reproducibility                       │
 └──────────────────────────────────────────────────────────────────────┘
```

The eight modules each address one of the field gaps identified in the prior research synthesis. They sit in parallel, share the lower layers, and are orchestrated either by direct invocation (for power users) or by the Conductor agent (for everyone else).

The **canonical data flow** for the headline use case ("user submits SMILES, gets polymorph risk profile") is:

1. Conductor parses the user request and constructs a plan.
2. OPENBENCH executes the plan, calling sub-modules:
3. GENESIS proposes candidate structures, augmented by HYDRA and MULTIPLEX where relevant.
4. DISARRAY flags candidates that should be modelled as disordered ensembles.
5. FOUNDRY ranks candidates using MLIPs.
6. KINETICA computes nucleation barriers and selection probabilities.
7. PROCESS contextualises results against typical crystallisation conditions.
8. INSIGHT attaches uncertainty and explanation per prediction.
9. Conductor synthesises the report.

Each step writes to LEDGER. Anything that touches an experimental queue passes through LAB BRIDGE. ANVIL runs continuously in the background to detect regression.

---

## 4. The eight modules

The naming convention: each module gets a single-word name and a one-line tagline. Internal sub-systems get descriptive names. We avoid acronym soup.

### 4.1 KINETICA — Kinetics and nucleation engine

> *"Which polymorph will actually form, not merely which is most stable."*

**Problem.** Standard CSP returns a thermodynamic ranking of polymorphs. The Ritonavir crisis was *not* a thermodynamic surprise — Form II had always been more stable. It was a *kinetic* surprise: nucleation conditions in the manufacturing plant finally crossed the barrier. Closing this gap is the single highest-impact problem in the field.

**Current SOTA we build on.** ML-derived collective variables for enhanced sampling (Salvalaglio's GNN-based CVs at UCL/XtalPi, Tiwary's SGOOP+metadynamics, the LeaPP framework, Information-Entropy CVs from Parrinello). Path-integral approaches for nucleation rates. Polymorph-specific Steinhardt parameters and graph latent variables.

**Technical approach.** Three sub-systems:

*PathFinder* — automated discovery of polymorph-discriminating collective variables. Given a CSP landscape from GENESIS or OPENBENCH, train a graph autoencoder to find low-dimensional CVs that separate polymorph basins. Validated against known systems (urea, glycine, paracetamol, ROY, mannitol).

*RareEvent* — well-tempered metadynamics + OPES + forward flux sampling, all driven by FOUNDRY MLIPs, biased along PathFinder CVs. Outputs polymorph-to-polymorph free energy barriers and per-polymorph nucleation work.

*SelectionMap* — given a target solvent, supersaturation, temperature, and seed/no-seed condition, returns a probability distribution over which polymorph nucleates. This is the headline output. Initially calibrated empirically against the experimental polymorph databases of paracetamol, ROY, glycine, mannitol, and tolfenamic acid.

**Inputs.** Set of candidate crystal structures (CIF), molecular topology, solvent identifier (SMILES), thermodynamic conditions (T, P, RH, supersaturation), optional seed structure.

**Outputs.** Per-polymorph nucleation work (kJ/mol), inter-polymorph transition barriers, selection probability distribution, recommended order of polymorph appearance under the given conditions.

**Dependencies.** FOUNDRY (for forces and energies during MD), PROCESS (for solvent-aware free-energy corrections), OPENBENCH or GENESIS upstream for candidates.

**Validation strategy.** Retrospective: predict the experimentally observed appearance order of polymorphs for ten well-characterised pharmaceutical systems; require ≥80% correct ordering. Prospective: collaborate with one academic crystallisation lab (probably Strathclyde CMAC or UCL) for blind tests on three molecules.

**Phasing.** v1: PathFinder + RareEvent for rigid molecules with ≤6 torsions, neat-system. v2: SelectionMap with explicit solvent. v3: heteronucleation (polymer/surface-induced).

**Hardest open problem.** Solvent dynamics during nucleation are still computationally brutal even with MLIPs. Implicit solvent corrections from COSMO-RS may have to suffice for v1.

---

### 4.2 DISARRAY — Disorder modelling

> *"Crystals lie still in textbooks; in real vials they jiggle."*

**Problem.** Many real pharmaceutical crystals are disordered: partial occupancy, orientational disorder, layer stacking faults. The CCDC's CEO explicitly named disorder prediction as the top open problem after the 7th Blind Test. Ritonavir Form 4, only solved in 2025, is itself disordered. Current CSP treats every candidate as a static, fully-ordered structure, and silently fails on disordered ones.

**Current SOTA we build on.** Configurational ensemble methods from inorganic CSP (Hong et al. 2020 NNP-from-disorder). RNN-based disorder probability models (Jakob et al. 2026). Genuinely little for organic crystals — this is genuine green field.

**Technical approach.** Three sub-systems:

*DisorderProb* — a model that, given a 2D molecular graph and a candidate ordered structure, predicts the probability that the experimentally realised crystal will exhibit positional, orientational, or compositional disorder. Trained on the CSD's disorder annotations.

*Ensemble* — given a candidate that DisorderProb flags as likely-disordered, generate a configurational ensemble (substituted, rotated, displaced) of low-energy near-degenerate variants and compute a configurational entropy contribution to free energy. This is essentially supercell sampling adapted for organic crystals.

*StackingFault* — a specialised solver for layer/stacking disorder common in flat-molecule pharmaceuticals (carbamazepine, sulfathiazole). Uses a 2D-periodic search over stacking offsets.

**Inputs.** Ordered candidate structure (CIF), molecular graph, optional experimental PXRD pattern (which often tells you whether disorder is present even when the structure is unsolved).

**Outputs.** Disorder probability and type, configurational ensemble (set of CIFs with weights), entropy correction to free energy, simulated PXRD with appropriate peak broadening.

**Dependencies.** FOUNDRY (energies), DATAHUB (CSD disorder labels for training), LAB BRIDGE (PXRD ingestion).

**Validation strategy.** Retrospective on a curated list of ~50 known disordered pharmaceutical structures. Cross-validation: predicted entropy corrections must improve free-energy ranking on the Firaha 2023 benchmark (or at least not degrade it).

**Phasing.** v1: DisorderProb classifier only. v2: Ensemble. v3: StackingFault.

**Hardest open problem.** The training labels in the CSD are crystallographer-annotated and inconsistent. Building a clean, audited label set is itself a contribution to the field, and probably needs to be a public sub-deliverable.

---

### 4.3 MULTIPLEX — Multi-molecule asymmetric units (Z′ > 1)

> *"Sometimes molecules pack two-by-two, and current CSP can't handle it."*

**Problem.** ~10% of organic crystals have more than one molecule in the asymmetric unit. The 7th Blind Test had a Z′ = 3 target; only six of twenty-eight groups predicted Z′ = 3 structures, mostly because of computational cost and search-space combinatorics. The current Schrödinger and Lavo pipelines are explicitly Z′ = 1 only. This blind spot can cost a polymorph entirely.

**Current SOTA we build on.** Topology-aware structure generation methods (Iuzzolino et al. 2024 Nature Communications); evolutionary CSP that allows variable Z′; Salvalaglio's molecular synthon analysis; pseudo-symmetry detection from the CSD.

**Technical approach.** Two sub-systems:

*HighZ-Search* — a variant of the standard packing search that biases sampling toward Z′ ∈ {2, 3, 4} configurations. Uses the CSD-trained "Z′ propensity classifier" to decide the search budget per Z′ for each input molecule. Molecules predicted to be Z′ = 1-only (rigid, symmetric, simple H-bonding) skip high-Z′ search; molecules with chirality, awkward shape, or competing H-bond donors get a higher Z′ budget.

*PseudoSymmetry* — a post-hoc detector that finds candidate structures sitting near the boundary between two space groups, which are common false-conglomerate cases that lead to surprise polymorphs.

**Inputs.** Molecular structure (SMILES + 3D conformer), Z′ search budget (default determined automatically).

**Outputs.** Z′ > 1 candidate structures, pseudo-symmetry flags, an honest report of which Z′ were searched and which were skipped.

**Dependencies.** GENESIS or OPENBENCH for the underlying generator; FOUNDRY for ranking.

**Validation strategy.** Retrospective on the curated Steed-group high-Z′ dataset and the 7th Blind Test Target XXXIII (Z′ = 3.8). Forward: predict five "Z′-suspicious" molecules from the high-Z′ shikimate ester family.

**Phasing.** v1: Z′ ≤ 2. v2: Z′ ≤ 4. v3: variable Z′ within a single search.

**Hardest open problem.** The combinatorics scale brutally. Z′ = 4 means 4× the conformational dimensions, plus 4× the relative-orientation dimensions. Even with MLIPs this is at the edge. Smart sampling (active learning, Bayesian optimisation over Z′) is mandatory, not optional.

---

### 4.4 HYDRA — Hydrates, solvates, salts, and co-crystals

> *"The drug is not always alone in its lattice."*

**Problem.** A huge fraction of pharmaceutical solid forms incorporate co-formers: water (hydrates), solvent molecules (solvates), counter-ions (salts), or other small molecules (co-crystals). These are the bulk of FDA-approved solid forms — paracetamol monohydrate, naproxen sodium, the mebendazole salts. Current open-source CSP does not handle them. Schrödinger has stated they will, "in the future". HYDRA is the open answer.

**Current SOTA we build on.** Knowledge-based hydrate/solvate propensity models (Takieddin et al., Abramov 2025 hybrid model); COSMO-RS thermodynamic compatibility scoring; Graph Attention Networks for solvate prediction (Sun et al. 2025); cocrystal screening via lattice energy comparison; Hydrogen Bond Propensity (CSD-Materials).

**Technical approach.** Four sub-systems:

*FormerScreen* — given an API SMILES and a list of candidate formers (water + 60 common solvents + a curated coformer library), score the thermodynamic likelihood of each forming a solid form. Combines COSMO-RS, HBP, and a graph-attention model trained on the CSD's multi-component entries.

*MultiCSP* — adapted packing search that places the API molecule and a former in the asymmetric unit at variable stoichiometry (1:1, 2:1, 1:2 for cocrystals; integer water counts for hydrates). Same downstream ranking as the homo-molecular pipeline.

*RHStability* — given a hydrate prediction, compute its stability as a function of relative humidity using the Firaha-style TRHu(ST) protocol re-implemented atop FOUNDRY MLIPs. This is critical: the FDA cares about hydrate stability under storage conditions, and "the API will deliquesce in Bogotá" is a real failure mode.

*SaltCSP* — adapted for charge-bearing systems (proton transfer, counter-ion choice). Uses a separate MLIP fine-tune trained on charged organic crystals (a subset of OMC25 contains them, and a community fine-tune is feasible).

**Inputs.** API SMILES; optional co-former list (defaults to curated screen of ~80 formers); optional target stoichiometry; conditions (T, RH).

**Outputs.** Ranked list of (former, stoichiometry, structure) triples with associated free energies and stability ranges.

**Dependencies.** FOUNDRY (especially the charged-system fine-tune for SaltCSP); GENESIS or OPENBENCH for sampling; PROCESS for solvent compatibility.

**Validation strategy.** Retrospective on the 13 multi-component posaconazole forms; the curcumin solvate set (Widauer et al. 2026); the well-characterised theophylline–water phase diagram.

**Phasing.** v1: FormerScreen + 1:1 cocrystals + monohydrates. v2: variable stoichiometry, salts. v3: ternary systems (API + water + cosolvent).

**Hardest open problem.** Salts involve proton transfer, which short-range MLIPs handle poorly. May need explicit polarisable ML potentials (MACE-POLAR-1, Feb 2026) — schedule SaltCSP for after MACE-POLAR-1 stabilises.

---

### 4.5 GENESIS — End-to-end generative model for organic crystals

> *"Skip the search; let the model propose."*

**Problem.** Hierarchical CSP (sample → relax → rank) is computationally expensive even with MLIPs. End-to-end generative models (diffusion, flow-matching, autoregressive) can in principle propose plausible polymorphs in a single pass at near-zero compute. MatterGen, DiffCSP, FlowMM have demonstrated this on inorganic materials. There is no equivalent for drug-like molecular crystals — the field has been waiting for OMC25 (released August 2025) to enable training. We move now.

**Current SOTA we build on.** MatterGen architecture (Microsoft, 2025); DiffCSP / DiffCSP++ joint equivariant diffusion; FlowMM Riemannian flow matching; CrystalLLM-style autoregressive baselines; the OMC25 dataset itself.

**Technical approach.** Three sub-systems:

*OrganicGen-D* — a periodic-equivariant diffusion model trained on OMC25 + CSD subset, conditioned on the input molecular graph. Outputs candidate unit cells with atomic positions. Inspired by DiffCSP++ but extended for the molecular-graph constraint and longer-range dispersion.

*PropertyConditioned* — a variant that conditions on target properties (density range, solubility class, hydrogen-bonding motif). Useful for the inverse-design use case ("give me a polymorph more soluble than Form I").

*Reranker* — generative models hallucinate. The reranker takes top-K outputs from OrganicGen-D, runs them through FOUNDRY for short relaxation, and produces a clean, deduplicated, energy-ranked candidate list.

**Inputs.** Molecular graph (SMILES); optional property conditioning vector; number of candidates K (default 1000).

**Outputs.** K candidate unit cells with relaxed coordinates and rough lattice energies.

**Dependencies.** OMC25 (DATAHUB hosts a clean version); FOUNDRY for the reranker.

**Validation strategy.** Coverage: generate 1000 candidates for each of the seven 7th-Blind-Test targets; verify ≥95% of experimental polymorphs are within 0.3 Å RMSDn of some candidate. Speed: full GENESIS landscape for a drug-like molecule in <30 GPU-minutes on an A100. Quality: top-50 candidates contain the experimental form for ≥80% of the OPENBENCH benchmark set.

**Phasing.** v1: OrganicGen-D unconditional, Z′ = 1, rigid-ish molecules. v2: property-conditioned. v3: handles Z′ > 1, multi-component (replaces parts of MULTIPLEX/HYDRA samplers).

**Hardest open problem.** Generative models are notorious for missing low-energy basins (mode collapse). Combining GENESIS with the systematic search of OPENBENCH is the safety net. The honest position: GENESIS is a *seed source*, not a *replacement* for systematic CSP — at least until extensive retrospective validation says otherwise.

---

### 4.6 PROCESS — Crystallisation-process digital twin

> *"From SMILES to scaled-up batch with a probability distribution at every step."*

**Problem.** Even a perfect polymorph energy ranking does not tell a process chemist *how to actually make Form II*. Current digital twins for crystallisation (gPROMS-based, Leeming et al. 2023) handle a single known polymorph well but cannot integrate polymorph selection. The bridge between "structure prediction" and "process prediction" is largely empty.

**Current SOTA we build on.** gPROMS / Siemens-PSE crystallisation models; the CMAC / Strathclyde "digital design" framework (Hare et al.); population balance modelling (PBM) with growth/nucleation kinetics; COSMO-RS solubility prediction; the Pharmaceutical Digital Design vision paper (2024 Cryst. Growth Des.).

**Technical approach.** Four sub-systems:

*SolubilityNet* — a fast neural surrogate for COSMO-RS, trained on a reasonable subset of curated solubility data. Predicts API solubility in 60+ solvents at multiple temperatures from SMILES alone. Uncertainty-aware.

*KineticsBridge* — couples KINETICA's nucleation-rate predictions with classical PBM. Inputs: polymorph candidates + KINETICA outputs + solvent. Outputs: time-resolved population of each polymorph during cooling/anti-solvent/evaporation crystallisation.

*ProcessOptimiser* — given a target polymorph and a list of acceptable process variables, recommends a cooling profile, anti-solvent addition rate, or seeding strategy that maximises the probability of the target. Uses Bayesian optimisation over PBM simulations.

*RiskScorer* — the final headline output. Given an API and its current commercial polymorph, returns a "ritonavir score": probability of an unexpected, more-stable polymorph appearing under any plausible plant condition, with expected impact on solubility/bioavailability.

**Inputs.** API + candidate polymorphs from upstream + process variable ranges + (optional) target form.

**Outputs.** Time-resolved polymorph populations, recommended process parameters, risk score with uncertainty.

**Dependencies.** KINETICA (nucleation rates), HYDRA (solvent compatibility, hydrate risk), DATAHUB (solubility training data).

**Validation strategy.** Retrospective digital-twinning of three documented industrial crystallisations (paracetamol Form II, succinic acid β-form, olanzapine). Prospective: collaborate with one academic pilot-scale crystalliser (Leeds, Strathclyde, MIT) for blind tests on novel APIs.

**Phasing.** v1: SolubilityNet + simple cooling-crystallisation PBM. v2: KineticsBridge + ProcessOptimiser. v3: anti-solvent and continuous crystallisation.

**Hardest open problem.** Industrial crystallisation data is mostly proprietary. We will need either (a) an industrial consortium partner willing to release de-identified data, or (b) careful synthesis of public literature data into a reproducible benchmark. This is as much an organisational problem as a technical one.

---

### 4.7 OPENBENCH — The integrating reference pipeline

> *"One command. One molecule in. A polymorph risk profile out."*

**Problem.** Even if KINETICA, GENESIS, and the others all work in isolation, an independent researcher with one A100 cannot use them. There needs to be a single end-to-end pipeline that runs gracefully on modest hardware, uses sane defaults, and produces a publication-grade polymorph landscape report. This is what FastCSP started; OPENBENCH finishes it.

**Current SOTA we build on.** FastCSP (Aug 2025, Meta + CMU + Marom group); Genarris 3.0; PyXtal; the SPaDe-CSP hyperparameter heuristics (Waseda, Oct 2025); HTOCSP (Good Chemistry, 2024).

**Technical approach.** OPENBENCH is the *glue*. It consists of:

*Pipeline* — a Python orchestrator with three modes: `quick` (single GPU, 30 min, MACE-OFF only, Z′ = 1, top 20 candidates), `standard` (1 A100, 6 hours, full hierarchy with DFT re-rank of top 50, all of MULTIPLEX/HYDRA), `thorough` (multi-GPU, 24+ hours, includes KINETICA dynamics).

*Defaults* — well-curated, opinionated defaults for every parameter. The user specifies a SMILES; everything else has a sensible default with documented rationale.

*Reporter* — produces a self-contained HTML report with the energy landscape, per-polymorph diagnostics, simulated PXRD patterns, INSIGHT-derived confidence scores, and a plain-language risk summary.

*Cloud-Adapter* — supports running in the same way on RunPod, Vast.ai, AWS Batch, or local SLURM. We do not write yet another job scheduler; we wrap existing ones.

**Inputs.** SMILES (or molecular file); mode (`quick` / `standard` / `thorough`); optional advanced flags.

**Outputs.** Polymorph landscape (CIF + energies), HTML report, machine-readable JSON of every prediction, full LEDGER provenance.

**Dependencies.** Everything. OPENBENCH is the integrator.

**Validation strategy.** Continuously benchmarked against the Lavo-NN benchmark (49 drug-like molecules), CPOSS209, and the 7th Blind Test. Continuous integration runs the `quick` mode on the Lavo benchmark on every commit; full `standard` runs nightly on a rotating subset.

**Phasing.** v1: `quick` mode + reporter, Z′ = 1, MACE-OFF only. v2: `standard` mode integrating MULTIPLEX, HYDRA, DISARRAY. v3: `thorough` mode integrating KINETICA and PROCESS.

**Hardest open problem.** Defaults. The wrong default makes the tool dangerous (silent failure). Curating defaults across the 230 space groups, the wide range of drug-like molecules, and three computational modes is a sustained, careful job that needs domain expertise embedded in the team.

---

### 4.8 INSIGHT — MLIP interpretability and uncertainty

> *"Trust, but verify what the model is actually paying attention to."*

**Problem.** MLIPs ranked structures correctly in the 7th Blind Test, but we have very little understanding of *why* they succeed or fail. A flat lattice-energy landscape (kJ/mol differences between polymorphs!) is exactly the regime where small systematic errors in a neural network destroy ranking. A pharma user submitting their proprietary candidate molecule needs to know whether the model is on familiar ground or hallucinating. The mechanistic interpretability of MLIPs in this domain is a wide-open frontier and, frankly, the place where this team's unique research background is most differentiating.

**Current SOTA we build on.** GNN attribution methods (SEAL, fragment-wise interpretability, Shapley sampling); zero-shot generalisation diagnostics for MLIPs (Ben Mahmoud et al. 2025); active-learning uncertainty estimation; the broader interpretability literature from materials chemistry (Friederich, Reiser et al.).

**Technical approach.** Four sub-systems, deliberately mirroring the PsychProbe / behavioural-feature-vector philosophy:

*StructuredProbe* — a battery of curated polymorph-pair stimuli (known polymorph A vs. known polymorph B, where the relative stability is experimentally settled). For each MLIP in FOUNDRY, evaluate its predictions on this battery, decompose attribution per atom and per interaction type (electrostatic, dispersion, intramolecular). Results in a "behavioural fingerprint" of each MLIP: where does it agree with experiment, where does it systematically err.

*UncertaintyHead* — wraps each MLIP with calibrated uncertainty (deep ensembles, MVE, evidential, or BNN depending on the model). All energies and forces returned by FOUNDRY include a calibrated uncertainty.

*OOD-Detector* — flags whether the input molecule is in or out of distribution for each MLIP, by reference to the training set chemical space (OMC25 atom types, common functional groups, charged species, halogens). Returns a per-element confidence flag.

*CounterfactualExplainer* — for a given polymorph energy prediction, identifies the smallest change in the input structure that would flip the ranking. Useful for users and for finding model failure modes.

**Inputs.** Any prediction made by FOUNDRY; query molecule; (for StructuredProbe) the curated stimulus battery.

**Outputs.** Confidence per prediction; OOD flags; behavioural fingerprint of the model; counterfactual explanations.

**Dependencies.** FOUNDRY (it wraps it); DATAHUB (stimulus battery storage).

**Validation strategy.** Coverage: every prediction in OPENBENCH carries an INSIGHT confidence. Calibration: Brier score and reliability diagrams on the polymorph-pair benchmark. Discrimination: failures detected by INSIGHT must correlate with actual ranking errors on held-out test molecules.

**Phasing.** v1: UncertaintyHead + OOD-Detector. v2: StructuredProbe with public behavioural fingerprints of MACE-OFF, AIMNet2, UMA. v3: CounterfactualExplainer.

**Hardest open problem.** A clean, well-curated polymorph-pair stimulus battery does not yet exist. Building it (hundreds of curated pairs with verified experimental relative stability) is itself a contribution to the field, comparable to releasing CPOSS209.

**Why this matters strategically.** INSIGHT is what makes the rest of the suite *trustworthy*. It is also the module most likely to produce publishable mechanistic-interpretability research independent of the larger product effort, which is important for academic credibility and recruiting.

---

## 5. Cross-cutting infrastructure

The eight modules sit on a shared foundation. Each piece below is a standalone deliverable.

### 5.1 DATAHUB

A unified polymorph data layer combining:
- The Cambridge Structural Database (CSD): 1.3M+ structures, requires license but is the canonical experimental ground truth.
- OMC25: 27M molecular crystal structures with PBE+D3 labels (CC-BY 4.0).
- CPOSS209: 209 curated experimental + hypothetical polymorphs of 20 small pharmaceuticals.
- The 7th Blind Test database: 171,679 entries from 207 landscapes (CCDC-released).
- Curated experimental polymorph appearance data (paracetamol, ROY, mannitol, glycine, urea, ritonavir, rotigotine — the canonical demonstration systems).
- A new POLARIS-curated multi-component database (HYDRA-relevant).
- A new POLARIS-curated disorder annotation database (DISARRAY-relevant).
- A new POLARIS-curated polymorph-pair stimulus battery (INSIGHT-relevant).

Implementation: Postgres + object store (S3-compatible) for raw structures, with a Python client (`polaris.data`) providing typed access. CSD-licensed components are isolated behind an interface; non-licensed users get OMC25 + CPOSS + the POLARIS-curated subsets.

### 5.2 FOUNDRY

The MLIP and generative-model interface. Wraps:
- MACE-OFF (Cambridge / Csányi)
- AIMNet2 (CMU / Isayev)
- UMA (Meta FAIR)
- Lavo-NN (if API is made available; otherwise, a community-trained equivalent)
- MACE-POLAR-1 (when stable)
- the GENESIS-trained models

Through one uniform API: `model.energy_and_forces(structure)`, `model.relax(structure)`, `model.predict_with_uncertainty(structure)`. Adapter pattern; new MLIPs can be added in <100 lines. Includes automatic GPU/CPU dispatch and batch inference.

### 5.3 CONDUCTOR

The LLM agent layer. Plans, routes, summarises. Built on a local LLM for the fast path (Llama 3.3 70B served via vLLM) with optional escalation to Claude/GPT-4o for hard reasoning. Inspired by MAPPS, MatAgent, and CrystalAgent but with strict scope: Conductor *plans* and *reports*, it does not *do physics*. Physics happens in the modules. This is the safety layer that prevents LLM hallucination from contaminating predictions.

Agent capabilities: parse user requests, choose modules and modes, monitor jobs, draft reports, answer follow-up questions about results. Refuses tasks it cannot validate.

### 5.4 ANVIL

Continuous benchmarking. Three benchmark tiers:
- *Smoke*: 5 simple molecules (aspirin, paracetamol Form I, urea, glycine α, naphthalene), every commit.
- *Standard*: Lavo-NN benchmark (49 molecules), nightly.
- *Stress*: 7th Blind Test + CPOSS209 + curated multi-component set, weekly.

Outputs: dashboards, regression alerts, public leaderboard. The leaderboard is itself a community good, comparable to the Matbench effort.

### 5.5 LAB BRIDGE

Interfaces to experimental data sources:
- PXRD ingestion (raw .xy or .xrdml files → structure-matching against POLARIS landscapes).
- Automated screening platforms (Unchained Labs Stuntman, Crystal16, Mettler-Toledo OptiMax) via standardised CSV/JSON exports.
- LIMS interfaces for labs that have them.
- Outbound queue: predictions can be submitted to a partner lab for blind validation.

### 5.6 LEDGER

Provenance tracking. Every output carries:
- Hash of all model weights used.
- Hash of all input data.
- Software version (POLARIS git SHA + dependencies).
- Compute environment (CPU/GPU model, OS).
- Wall-clock time and cost.

Ledger entries are append-only and signed. Re-running any computation by quoting only its ledger ID must reproduce the result bit-for-bit.

---

## 6. Use-case scenarios

How the suite actually serves users.

### Scenario A — De-risking a drug candidate

**Persona.** A medicinal chemist at a mid-sized pharma company has a lead compound, two months from IND filing.

**Flow.** They submit the SMILES through a web UI (which runs on top of OPENBENCH `standard` mode). 6 hours later, they receive an HTML report showing: 12 plausible polymorphs ranked by free energy, 3 likely hydrates, 2 disorder-prone candidates flagged by DISARRAY, a "ritonavir score" of 0.3 from PROCESS (medium risk), and a recommendation to experimentally screen Form II + the dichloromethane solvate with priority.

**Total compute cost on Vast.ai.** ~$8 on a single A100. Versus ~$50K and 6 weeks for a commercial CSP study.

### Scenario B — Process optimisation

**Persona.** A process chemist trying to reliably crystallise the Form II of an established API in a new manufacturing site.

**Flow.** They feed the existing polymorph landscape (already computed) into PROCESS's `ProcessOptimiser`, with constraints (water + ethanol mixture acceptable; jacket temperature 5–60°C). PROCESS returns a recommended cooling profile (0.5°C/min from 50°C to 10°C) with seed addition at 35°C, plus the predicted yield of Form II vs. Form I as a function of supersaturation.

### Scenario C — Researcher developing a new MLIP

**Persona.** An academic group has trained a new MLIP for halogenated organics.

**Flow.** They register the model with FOUNDRY (a standard adapter), run ANVIL benchmarks against it, and immediately see how their model ranks against MACE-OFF and AIMNet2 on the public leaderboard. INSIGHT generates a behavioural fingerprint comparing the new model to the established ones. If the model wins, it gets adopted by OPENBENCH; if not, the research group has detailed diagnostics about *where* it falls short.

### Scenario D — The public-health moonshot

**Goal.** Compute polymorph risk profiles for every small-molecule drug on the FDA Orange Book (~4,000 active ingredients) and publish them.

**Flow.** A coordinated run of OPENBENCH `standard` mode across all 4,000 molecules. Estimated compute: ~20K A100-hours (~$30K on spot). Output: a public database, indexed by drug, of predicted polymorphs, hydrate stability under typical climates, and risk scores. This is the AlphaFold-database moment for polymorphism.

**Strategic value.** It produces the dataset that lets epidemiologists, formulators, regulators, and patients ask: "is my drug at risk of a Ritonavir event?". It is the kind of output that drives FDA guidance changes.

### Scenario E — Closed-loop autonomous screening

**Persona.** A research group with an automated screening platform (e.g., the high-throughput PXRD robotic workflow described in the literature) and a wishlist of 50 molecules.

**Flow.** POLARIS Conductor designs an experimental campaign for each molecule (which solvents, temperatures, anti-solvents), the platform runs it, PXRD patterns flow back through LAB BRIDGE, structure-matching against POLARIS landscapes confirms or denies hits, and PROCESS updates its kinetic models with the experimental observations. The loop closes overnight.

---

## 7. Phased roadmap

A 36-month plan that can be parallelised by module sub-team. Each "vN" means a public release.

**Months 0–3: Foundations.**
- DATAHUB v0: ingest OMC25, CPOSS209, set up storage.
- FOUNDRY v0: wrap MACE-OFF and AIMNet2.
- ANVIL v0: smoke benchmarks running.
- LEDGER v0: hash and persist any computation.
- OPENBENCH v0: end-to-end "quick" mode (Z′ = 1, MACE-OFF, top 20). This is the first releasable artefact.

**Months 3–6: Vertical slice.**
- INSIGHT v1: UncertaintyHead, OOD-Detector.
- DISARRAY v1: DisorderProb classifier.
- MULTIPLEX v1: Z′ ≤ 2 in OPENBENCH.
- HYDRA v1: FormerScreen + 1:1 cocrystals + monohydrates.
- OPENBENCH v1: "standard" mode released. **This is the headline public release.**

**Months 6–12: Kinetics and process.**
- KINETICA v1: PathFinder + RareEvent for rigid molecules.
- PROCESS v1: SolubilityNet + simple PBM.
- CONDUCTOR v1: planning agent with LLM router.
- INSIGHT v2: StructuredProbe with first behavioural fingerprints.
- LAB BRIDGE v1: PXRD ingestion.

**Months 12–18: Generative and advanced.**
- GENESIS v1: OrganicGen-D unconditional.
- KINETICA v2: SelectionMap with explicit solvent.
- HYDRA v2: variable stoichiometry, salts.
- DISARRAY v2: configurational ensemble.
- OPENBENCH v2: "thorough" mode integrating KINETICA.

**Months 18–24: Integration and validation.**
- PROCESS v2: KineticsBridge + ProcessOptimiser + RiskScorer.
- GENESIS v2: property-conditioned.
- MULTIPLEX v2: Z′ ≤ 4.
- The first published prospective blind test on novel molecules.

**Months 24–36: The moonshot.**
- Compute the FDA Orange Book polymorph database.
- Publish a flagship Nature / Science paper with retrospective + prospective validation.
- Establish a permanent governance structure for the open-source consortium.

---

## 8. Validation and benchmarking strategy

Three principles drive validation:

**(i) Always retrospective before prospective.** Before claiming any module works, we must reproduce known systems. The retrospective set is non-negotiable: paracetamol, aspirin, ROY (10 polymorphs), ritonavir (4 polymorphs), rotigotine, mannitol, glycine, urea, tolfenamic acid, sulfathiazole, carbamazepine. Any release that regresses on this set is blocked.

**(ii) Public leaderboards.** ANVIL publishes benchmark results continuously. We do not hide failures. This is critical for credibility and is also how we recruit external contributors.

**(iii) Prospective blind tests with academic partners.** At minimum two published prospective studies before the public moonshot. Likely partners: CMAC (Strathclyde), Day group (Southampton), Marom group (CMU), Salvalaglio group (UCL), Cruz Cabeza group (Manchester).

**Specific benchmarks per module:**
- KINETICA: appearance order on 10 systems; ≥80% correct ordering.
- DISARRAY: classification AUC ≥ 0.85 on the disorder annotation set.
- MULTIPLEX: recover all Z′ > 1 polymorphs from the 7th Blind Test; <2× cost penalty over Z′ = 1.
- HYDRA: recover ≥90% of monohydrate experimental structures in the test set.
- GENESIS: recall@50 ≥ 0.80 on the OPENBENCH benchmark; sub-30-minute generation on A100.
- PROCESS: digital twin recovery of three documented industrial crystallisations within 10% on yield.
- OPENBENCH: full Lavo benchmark recovery in `standard` mode; matches Schrödinger 2025 paper accuracy.
- INSIGHT: calibration Brier score ≤ 0.1 on the polymorph-pair set.

**The "Ritonavir test."** A unifying integration test, run before every major release: if we feed POLARIS the SMILES of ritonavir, with no other information, does the `standard` pipeline (a) generate Form II within the top 5 candidates, (b) rank it as more stable than Form I at room temperature, (c) flag the solubility implications, (d) flag a high "ritonavir score" risk? Anything that breaks this test blocks the release.

---

## 9. Risks, dependencies, and open questions

**Technical risks.**

*Foundation MLIPs may stop scaling.* MACE-OFF, AIMNet2, UMA could plateau before reaching the kJ/mol accuracy needed for confident polymorph ranking. Mitigation: INSIGHT detects this; we cite uncertainty honestly; we maintain DFT re-rank capability indefinitely.

*Generative models may underperform hierarchical CSP.* GENESIS is the highest-variance bet. Mitigation: it is an *additive* candidate source, not the only one. OPENBENCH always also runs systematic search.

*Z′ > 4 may be intractable.* Mitigation: accept the limit; document it; flag high-Z′-prone molecules early.

*Salts (proton transfer) may need full electronic-structure calculations.* Mitigation: schedule SaltCSP after MACE-POLAR-1 stabilises (Q3 2026 at earliest).

**Data risks.**

*CSD licensing.* Some users (especially academic groups in the global south) cannot afford CSD licences. Mitigation: every POLARIS feature has a non-CSD path that uses OMC25 + the curated POLARIS subsets. The CSD path is purely additive.

*Industrial process data is proprietary.* PROCESS validation is the most affected. Mitigation: build relationships with one or two pre-competitive consortia (CMAC has form here); use literature-derived benchmarks otherwise.

**Organisational risks.**

*Single-team coordination.* Eight modules + cross-cutting layers is a lot. Mitigation: enforce module-level ownership; weekly integration checkpoints; CI tests across module boundaries.

*Funding sustainability.* Open-source maintenance is a known graveyard. Mitigation: adopt a foundation/consortium model from the start (think Linux Foundation or NumFOCUS), with industrial members paying for support and training rather than for the software itself.

**Open scientific questions** (where the answer should drive design but is not yet settled):

- Is target-specific MLIP fine-tuning (AIMNet2-style) better than universal MLIPs (UMA-style) for production CSP? Probably depends on chemistry; INSIGHT will help us decide per-molecule.
- How much of the "wrong polymorph at room temperature" problem is kinetic vs. thermodynamic-error? The Firaha 2023 protocol assumes mostly thermodynamic; KINETICA will let us check.
- For generative models, is conditioning on the molecular graph sufficient, or do we need the 3D conformer? GENESIS will run an ablation.
- Should INSIGHT report uncertainty in absolute terms or in *ranking* terms? Polymorph users care almost only about ranking.

---

## 10. Why this matters

The Ritonavir crisis cost Abbott hundreds of millions of dollars and left HIV patients without their medication for two years. Rotigotine had a similar episode. There are documented cases for ranitidine, abacavir, and others. The 15–45% number from Neumann's analysis means that, statistically, several drugs in any given person's medicine cabinet are sitting in metastable forms whose more stable polymorph has not yet been discovered.

Polymorph prediction is a public health asset. The current state — closed-source GRACE, closed-source Schrödinger, closed-source Lavo, all priced for big pharma — is a market failure. Generic manufacturers cannot afford it. Academic researchers in the global south cannot run it. Regulatory agencies cannot independently verify it.

POLARIS is the open infrastructure that fixes this. The technical pieces exist. The data exists. The compute is cheap on the spot market. What is missing is the integration, the validation, and the political will to build it as a public good.

The team building this should expect three classes of impact:

1. **Scientific.** Publications across CSP, MLIP interpretability, kinetics, and generative materials. A flagship demonstration paper. New benchmarks that the field rallies around.

2. **Industrial.** Adoption by pharma as a complement to (and eventually replacement for) commercial tools. Adoption by CRO labs. Adoption by generic manufacturers who currently cannot do CSP at all.

3. **Public-health.** A public, FDA-relevant database of polymorph risk profiles. Earlier detection of disappearing-polymorph events. Reduction in drug shortages caused by polymorphism issues.

The window is now. OMC25 just unlocked the data. The MLIPs just hit the accuracy threshold. The Ritonavir paper just provided the rhetorical hook. The next two years will determine who builds this infrastructure and on what terms. We propose to build it open.

---

## Appendix A — Tool inventory we build on

The suite stands on a substantial existing ecosystem. Every component below is preserved in some form, either as a direct dependency or as a comparison baseline.

**Sampling / generation.** PyXtal, Genarris 3.0, USPEX (free for academics), CALYPSO (ditto), CrySPY, AIRSS, XtalOpt.

**MLIPs.** MACE-OFF, AIMNet2, UMA (Meta FAIR), Lavo-NN, ANI-2x, MACE-POLAR-1.

**Generative models.** MatterGen, DiffCSP, DiffCSP++, EquiCSP, FlowMM, CDVAE.

**Free-energy methods.** Firaha-Neumann TRHu(ST), the FHI-aims PBE0+MBD pipeline, Day-group active-learning MLIPs from CSP landscapes.

**Enhanced sampling.** PLUMED 2, OPES, well-tempered metadynamics, SGOOP, the Salvalaglio GNN-CV framework, LeaPP.

**Process modelling.** gPROMS FormulatedProducts (commercial; baseline), PharmaMV, PBM literature implementations.

**Databases.** Cambridge Structural Database (CCDC), OMC25 (HuggingFace), CPOSS, the 7th Blind Test database, RRUFF (PXRD).

**Experimental interfaces.** Unchained Labs Stuntman, Crystal16, Mettler-Toledo, the autonomous PXRD robotic workflow.

**LLM tooling.** vLLM for local serving, OpenAI-compatible APIs, ChemCrow as a scaffold reference.

---

## Appendix B — Module dependency matrix

A quick reference for who depends on whom. Rows depend on columns.

|              | DATAHUB | FOUNDRY | OPENBENCH | KINETICA | DISARRAY | MULTIPLEX | HYDRA | GENESIS | PROCESS | INSIGHT |
|--------------|:-------:|:-------:|:---------:|:--------:|:--------:|:---------:|:-----:|:-------:|:-------:|:-------:|
| **OPENBENCH**| ●       | ●       | —         |          | ●        | ●         | ●     | ●       |         | ●       |
| **KINETICA** | ●       | ●       | ●         | —        |          |           |       |         | ◐       |         |
| **DISARRAY** | ●       | ●       |           |          | —        |           |       |         |         |         |
| **MULTIPLEX**| ●       | ●       | ●         |          |          | —         |       | ◐       |         |         |
| **HYDRA**    | ●       | ●       | ●         |          |          |           | —     |         | ◐       |         |
| **GENESIS**  | ●       | ●       |           |          |          |           |       | —       |         |         |
| **PROCESS**  | ●       | ●       |           | ●        |          |           | ●     |         | —       |         |
| **INSIGHT**  | ●       | ●       |           |          |          |           |       |         |         | —       |
| **CONDUCTOR**| ●       |         | ●         | ●        | ●        | ●         | ●     | ●       | ●       | ●       |

(● = hard dependency; ◐ = soft / optional)

OPENBENCH and CONDUCTOR are the two integrators. The leaf modules (KINETICA, DISARRAY, MULTIPLEX, HYDRA, GENESIS, PROCESS, INSIGHT) can each be built largely in parallel by independent sub-teams once DATAHUB and FOUNDRY exist.

---

## Appendix C — Glossary

*CSP* — Crystal Structure Prediction. The computational task of predicting the crystal forms a molecule will adopt, given only its 2D structure.

*Polymorph* — One of multiple possible crystal forms of the same molecule. Different polymorphs can have radically different solubility, stability, and bioavailability.

*Z′* — The number of independent molecules in the asymmetric unit of a crystal. Most CSP works at Z′ = 1; high-Z′ crystals account for ~10% of the CSD.

*MLIP* — Machine-Learned Interatomic Potential. A neural network that predicts energies and forces of atomic configurations, much faster than DFT but with comparable accuracy when properly trained.

*DFT* — Density Functional Theory. The standard quantum-mechanical method for computing energies of atoms and molecules. Accurate, slow, and the historical reference standard for CSP energy ranking.

*PXRD* — Powder X-Ray Diffraction. The dominant experimental technique for identifying polymorphs of solid samples.

*Free energy under realistic conditions* — Energy that accounts for temperature, pressure, and humidity, including phonon vibrational contributions. Essential for predicting which polymorph wins under storage conditions.

*Ritonavir score* — POLARIS-coined term for the predicted probability that an unforeseen, more-stable polymorph of an API will appear under plant-realistic conditions.

---

*End of architecture document. Version 0.1. To be revised as the build team begins prototyping and discovers what needs to change.*
