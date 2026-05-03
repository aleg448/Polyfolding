# Model Evaluation Protocol

This protocol governs MACE-OFF, AIMNet2, UMA, and future MLIP evaluations.

## Minimum Metadata

Every prediction file must record:

- `pair_id`
- `energy_a`, `energy_b`
- energy unit
- model name
- model version or checkpoint ID
- energy uncertainty per structure when available
- OOD score and OOD flag per structure when available

## Ranking Convention

Lower predicted energy is treated as more stable. Experimental ordering `A>B` means structure A is experimentally more stable than structure B.

## Headline Metrics

- Overall pairwise ranking accuracy on `verified` records.
- Ranking accuracy by chemistry tag and flexibility class.
- Calibration Brier score and expected calibration error when uncertainty is present.
- OOD-flagged failure rate.

## Reproducibility

Every headline report must include the manifest SHA-256, prediction-file SHA-256, CrystalProbe version, model versions, and generated ledger entry.

