# Historical Research Opportunities For CrystalProbe

This note maps older software, computing, simulation, and research-publication ideas to CrystalProbe modules that are now practical with modern compute, ML interatomic potentials, open data tooling, and continuous verification.

The point of view is deliberately hybrid: ambitious mission, conservative claims. Historical methods can inspire useful new tooling, but every implementation should still pass through CrystalProbe's candidate, reviewed, and verified evidence gates before it becomes a scientific claim.

## Working Thesis

CrystalProbe can be positioned as a modern reliability layer for molecular prediction: it revives proven ideas from crystal structure prediction, statistical simulation, uncertainty estimation, and reproducible research, then wraps them in source provenance, optional scientific backends, public artifacts, and explicit claim gates.

That is a stronger publication thesis than "we built another model." It says:

- Old problem: molecular prediction often produced plausible outputs before the outputs were auditable.
- Modern opportunity: cheap parallel inference, MLIPs, open-source packaging, CI, and structured metadata make audit-first prediction workflows feasible.
- CrystalProbe contribution: make reliability, evidence tiers, uncertainty, licensing, and reproducibility first-class objects.

## Opportunity Matrix

| Historical thread | Older source | What was hard then | Modern enabler | CrystalProbe implementation | Publication value | Claim risk |
|---|---|---|---|---|---|---|
| Community blind-test discipline for crystal structure prediction | Dunitz and Gavezzotti's crystal-predictability debate; CCDC blind tests such as Lommerse et al. 2000 and later blind-test reports | Expensive search, uneven methods, limited public automation, hard-to-compare evidence | MLIPs, reproducible public artifacts, structured evidence records | Add a small "blind-slice replay" mode: curated candidate structures, hidden/held-out labels where possible, candidate -> reviewed -> verified promotion, and public failure analysis | Makes CrystalProbe look like serious research infrastructure, not a demo | Do not imply new benchmark success until verified labels exist |
| Hydrogen-bond and packing-motif priors | Etter's hydrogen-bond preference rules and later crystallographic motif work | Manual chemical interpretation and limited automated motif extraction | CIF parsers, graph features, CSD/COD-derived metadata where licensed, deterministic SVG explanations | Add `motif_prior` features: donor/acceptor motifs, packing-contact summaries, and motif-aware error slices | Creates interpretable chemistry features a reviewer can inspect | Motif heuristics must remain explanatory signals, not proof of stability |
| Energy-landscape search and minima ranking | Metropolis Monte Carlo, simulated annealing, basin-hopping, replica exchange | Too many local minima, expensive relaxations, weak provenance around search paths | GPU execution, MLIP relaxation, cheap ensemble screening, structured ledgers | Add a "landscape audit" layer for candidate ensembles: basin diversity, duplicate detection, backend disagreement, and ranking stability | Complements FastCSP-style generation by auditing generated landscapes | CrystalProbe should not claim to be a full CSP engine unless generation is actually implemented |
| Free-energy estimation and enhanced sampling | Zwanzig free-energy perturbation, Bennett acceptance ratio, umbrella sampling, metadynamics, replica-exchange MD | Sampling was too slow for routine molecular-crystal comparison | MLIPs, parallel trajectories, small targeted probes, automated convergence checks | Add an optional `free_energy_probe` for tiny, labeled demonstrations: method metadata, convergence diagnostics, and abstention when uncertainty is too high | Bridges from static lattice-energy ranking toward thermodynamic relevance | Free-energy outputs require strict calibration and should start as demonstrations |
| Active learning and expensive black-box optimization | Query by committee and Efficient Global Optimization | Model evaluations were costly and experiments were manually chosen | Multi-backend disagreement, cheap queue scoring, automated source-acquisition ledgers | Add a triage policy that chooses the next best curation or backend job from uncertainty, disagreement, evidence gaps, and publication value | Shows practical ML engineering judgment: spend compute where evidence is weakest | Avoid optimizing for attractive plots instead of validated records |
| Bootstrap, conformal prediction, and calibrated abstention | Efron's bootstrap and Vovk/Gammerman/Shafer conformal prediction | Limited compute for resampling and fewer standard ML calibration workflows | Stored predictions, ensembles, repeated runs, CI-generated calibration reports | Add confidence intervals around ranking gaps and explicit abstention labels such as `needs_verified_evidence` | Aligns directly with "reliable open research tool" positioning | Calibration sets must be verified; candidate records cannot calibrate headline claims |
| Crystallographic file standards and databases | CIF standardization, Cambridge Structural Database, Crystallography Open Database | File exchange existed, but licensing, provenance, and automated validation were often downstream concerns | Machine-readable schemas, open data APIs, release-boundary checks, docs-as-tests | Strengthen source registries: public/open records, local-only CCDC/CSD records, license status, derived-artifact rules | Turns licensing honesty into a visible engineering strength | Never redistribute raw or coordinate-bearing gated data without explicit license review |
| Literate and reproducible computational research | Knuth's literate programming; Claerbout/Karrenbach and Buckheit/Donoho reproducible research | Rebuilding figures and results required fragile local environments | GitHub, CI, package metadata, deterministic SVGs, JSON manifests, executable demos | Treat every public figure and table as rebuildable from scripts; keep docs tested by integrity gates | Excellent fit for JOSS-style software publication and hiring review | Generated reports must not drift from live tests |
| Machine-learned interatomic potentials | Behler-Parrinello neural network potentials and GAP | Quantum-level energy surfaces were too expensive for broad search/sampling | MACE, AIMNet2, UMA, fairchem, optional backend adapters | Keep optional backend adapters, backend-readiness reports, and disagreement fingerprints | Shows modern compute is being used as a careful instrument, not magic | Absolute energies across backends are not automatically comparable |

## Highest-Impact Modules To Build From This

1. `historical_opportunity_matrix`: a machine-readable JSON companion to this document, with source, old blocker, modern enabler, implementation target, and claim gate for each idea.
2. `motif_prior`: CIF-derived donor/acceptor and packing-contact summaries that can explain why a candidate pair is chemically interesting before it is verified.
3. `active_evidence_triage`: a queue scorer that ranks the next curation, source-acquisition, backend, or reviewer task by expected claim-value reduction.
4. `landscape_audit`: a module that accepts candidate structures from any generator and reports duplicate forms, basin diversity, backend disagreement, and unsupported claims.
5. `free_energy_probe`: an optional, small-scale enhanced-sampling demonstration that records method metadata and abstains when convergence evidence is weak.
6. `calibrated_abstention`: bootstrap/conformal-style intervals for ranking gaps, but only trained or validated on reviewed/verified evidence.

## Implemented Surfaces

The first dependency-light implementation pass is source controlled:

- `data/curation/historical_opportunity_matrix_v0.1.json`: machine-readable opportunity matrix.
- `src/crystalprobe/insight/historical_opportunities.py`: ranks historical opportunities by publication value, readiness, and claim risk.
- `src/crystalprobe/insight/motif_prior.py`: computes motif-prior summaries from existing polymorph-pair annotations.
- `src/crystalprobe/insight/active_evidence_triage.py`: prioritizes evidence tasks without turning priority into a claim.
- `src/crystalprobe/insight/landscape_audit.py`: audits candidate landscapes for duplicate basins and backend winner disagreement.
- `src/crystalprobe/insight/free_energy_probe.py`: implements small Zwanzig and Bennett-style free-energy estimators with abstention.
- `src/crystalprobe/insight/evidence_packet.py`: combines motif, triage, prediction-abstention, source, and promotion blockers for one pair.
- `src/crystalprobe/insight/evidence_resolution.py`: records candidate literature and public source evidence that can resolve packet blockers without auto-promoting records.
- `src/crystalprobe/uncertainty/calibrated_abstention.py`: implements bootstrap intervals, conformal thresholds, and claim-gated abstention decisions.
- `scripts/build_historical_opportunity_report.py`, `scripts/build_active_evidence_triage_report.py`, and `scripts/build_historical_research_modules_report.py`: rebuildable reports for publication review.
- `scripts/build_evidence_packet_report.py`, `scripts/build_evidence_resolution_report.py`, and `scripts/run_research_cycle.py`: the first operational research-cycle runner, single-pair evidence packet, and candidate-only evidence-resolution layer.

## Best Publication Angle

The strongest near-term paper is not "CrystalProbe solves polymorph prediction." The stronger claim is:

> CrystalProbe is an open, claim-gated reliability layer for molecular-crystal prediction workflows, combining historical best practices from CSP blind tests, statistical simulation, uncertainty calibration, and reproducible research with modern MLIP backends and public artifact checks.

This angle is credible because it accepts the current evidence limits while showing a serious research program. It also connects directly to drug discovery: before molecular prediction can influence candidate selection, formulation risk, or experimental prioritization, the software has to prove provenance, uncertainty discipline, evidence quality, and reproducibility.

## Implementation Guardrails

- Keep `candidate`, `reviewed`, and `verified` labels visible in every output.
- Treat historical methods as implementation opportunities, not validation evidence.
- Prefer optional scientific backends when available, but make missing-backend states explicit.
- Keep CCDC/CSD-derived coordinates local-only unless license review permits release.
- Report backend disagreement as an inspection signal unless calibration evidence supports stronger language.
- Make every public table or figure rebuildable from a command.

## Source Links

- Dunitz and Gavezzotti debate: [Are crystal structures predictable?](https://pubs.rsc.org/en/content/articlehtml/2003/cc/b211531j)
- CCDC blind-test lineage: [Seventh blind test of crystal structure prediction](https://journals.iucr.org/b/issues/2024/06/00/aw5093/)
- First CSP blind test record: [A test of crystal structure prediction of small organic molecules](https://cir.nii.ac.jp/crid/1360292619250335104)
- Hydrogen-bond rules: [Etter hydrogen-bond preferences](https://pubs.rsc.org/en/content/articlepdf/1990/c3/c39900000589)
- Metropolis Monte Carlo: [Equation of state calculations by fast computing machines](https://doi.org/10.1063/1.1699114)
- Simulated annealing: [Optimization by Simulated Annealing](https://doi.org/10.1126/science.220.4598.671)
- Free-energy perturbation: [Zwanzig free-energy perturbation](https://doi.org/10.1063/1.1740409)
- Bennett acceptance ratio: [Efficient estimation of free energy differences](https://doi.org/10.1016/0021-9991(76)90078-4)
- Umbrella sampling: [Torrie and Valleau umbrella sampling](https://doi.org/10.1016/0021-9991(77)90121-8)
- Metadynamics: [Escaping free-energy minima](https://doi.org/10.1073/pnas.202427399)
- Replica Monte Carlo: [Swendsen and Wang replica Monte Carlo](https://doi.org/10.1103/PhysRevLett.57.2607)
- Replica-exchange molecular dynamics: [Sugita and Okamoto REMD](https://doi.org/10.1016/S0009-2614(99)01123-9)
- Basin-hopping: [Wales and Doye basin-hopping](https://doi.org/10.1021/jp970984n)
- Efficient Global Optimization: [Jones, Schonlau, and Welch EGO](https://doi.org/10.1023/A:1008306431147)
- Query by committee: [Seung, Opper, and Sompolinsky](https://collaborate.princeton.edu/en/publications/query-by-committee)
- Bootstrap: [Efron bootstrap](https://doi.org/10.1214/aos/1176344552)
- Conformal prediction: [Algorithmic Learning in a Random World](https://www.alrw.net/)
- Behler-Parrinello neural network potentials: [High-dimensional potential-energy surfaces](https://doi.org/10.1103/PhysRevLett.98.146401)
- Gaussian Approximation Potentials: [The accuracy of quantum mechanics, without the electrons](https://doi.org/10.1103/PhysRevLett.104.136403)
- CIF standard: [The Crystallographic Information File](https://www.iucr.org/__data/iucr/cif/standard/cifstd1.html)
- Crystallography Open Database: [COD open-access collection](https://academic.oup.com/nar/article/40/D1/D420/2903497)
- Literate programming: [Knuth, The Computer Journal](https://doi.org/10.1093/comjnl/27.2.97)
- Reproducible electronic documents: [Claerbout and Karrenbach summary](https://eurekamag.com/research/104/701/104701062.php)
- WaveLab and reproducible research: [Buckheit and Donoho](https://statistics.stanford.edu/technical-reports/wavelab-and-reproducible-research)
- JOSS software-publication expectations: [Submission requirements](https://joss.readthedocs.io/en/latest/submitting.html)
