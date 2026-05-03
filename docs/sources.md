# Source Registry

CrystalProbe should prefer open, redistributable sources and keep license status explicit at record level.

## CPOSS209

CPOSS209 is the first benchmark spine. The paper is "One Size Fits All? Development of the CPOSS209 Data Set of Experimental and Hypothetical Polymorphs for Testing Computational Modeling Methods" in *Crystal Growth & Design*.

- Paper DOI: https://doi.org/10.1021/acs.cgd.5c00255
- ACS page: https://pubs.acs.org/doi/10.1021/acs.cgd.5c00255
- Figshare dataset page: https://acs.figshare.com/articles/dataset/28883051

Before redistributing derived records, verify the license terms of the Figshare files and preserve attribution.

## OMC25

OMC25 is a large molecular-crystal DFT dataset for model development and OOD context, not the primary experimental stability benchmark.

- Hugging Face dataset: https://huggingface.co/datasets/facebook/OMC25
- FAIR Chemistry docs: https://fair-chem.github.io/molecules/datasets/omc25.html
- Scientific Data paper: https://www.nature.com/articles/s41597-026-06628-2

The data is described as CC-BY-4.0, but Hugging Face access approval may be required.

## MACE-OFF

MACE-OFF23 is exposed through the MACE ASE calculator.

- Foundation model docs: https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html
- ASE calculator docs: https://mace-docs.readthedocs.io/en/latest/guide/ase.html

Checkpoint licensing is not the same as this repository license; verify before packaging workflows around downloaded models.

## fairchem, UMA, and FastCSP

fairchem is the current integration point for Meta FAIR Chemistry models and molecular-crystal tasks.

- GitHub: https://github.com/facebookresearch/fairchem
- OMC25 model page: https://huggingface.co/facebook/OMC25
- OMC25 dataset page: https://huggingface.co/datasets/facebook/OMC25

UMA model access and checkpoint licenses must be handled explicitly.

