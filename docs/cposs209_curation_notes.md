# CPOSS209 Curation Notes

This note records the current CPOSS209 evidence state for CrystalProbe. It is not a benchmark manifest and must not be treated as final stability labeling.

## Source

- Article: Price, Paloni, Salvalaglio, and Price, "One Size Fits All? Development of the CPOSS209 Data Set of Experimental and Hypothetical Polymorphs for Testing Computational Modeling Methods", *Crystal Growth & Design*, 2025.
- DOI: https://doi.org/10.1021/acs.cgd.5c00255
- Open article page: https://pubs.acs.org/doi/10.1021/acs.cgd.5c00255
- Supplemental dataset page: https://acs.figshare.com/articles/dataset/28883051

The article describes CPOSS209 as 209 experimental and hypothetical crystal structures across 20 organic molecules and precursors. CrystalProbe currently indexes the local supplemental CIF archive as:

- `All_Psi_Crys.cif`: 209 crystal-optimized blocks.
- `All_Psi_Mol.cif`: 209 molecule-optimized blocks.
- `Additional_Psi_Mol.cif`: 4 additional molecule-optimized blocks.
- `All_Psi_Crys.cif` adjacent-form curation queue: 189 candidate pairs.
- `All_Psi_Crys.cif` all-pairs exploratory queue: 1127 candidate pairs.

## Stability Evidence State

The paper is useful for triaging stability curation, but it does not make every adjacent-form pair a verified benchmark label. The current safe interpretation is:

- Known enantiotropic or monotropic relationships are discussed for a minority of CPOSS families.
- The paper explicitly warns that free energies matter for stability ranking.
- Some families are currently considered monomorphic or resistant to interconversion.
- A large fraction of families still need primary-evidence review before CrystalProbe can label pairwise experimental ordering.

Specific relationships mentioned in the paper should be entered only after curator review against the cited primary references, not copied blindly from figure captions or narrative text.

## Initial Family Triage

Use this as a queue, not as final labels:

- High-priority stability review: `CRN`, `CBZ`, `MFA`, `FFA`, `SMZ`, `FLU`, `OXC`.
- Lower immediate ranking value: `PTH`, `SAC`, `FEA`, `IBP`, `NAP`, because the paper describes these as monomorphic or not readily interconverting.
- Remaining families: review source paper section and primary references before inclusion in ranking metrics.

## Promotion Rule

A CPOSS candidate pair can move into a CrystalProbe benchmark manifest only when it has:

- two source block IDs from the indexed CIF archive;
- human-readable form labels mapped to those block IDs;
- experimental stability ordering under named conditions;
- temperature or condition notes when relevant;
- DOI or durable URL for the primary stability evidence;
- explicit disorder/solvate/channel caveats;
- a license decision for redistributing any derived CIF subset.

Until then, keep the pair in generated candidate JSON under `outputs/` or in a curation work queue outside the released benchmark.
