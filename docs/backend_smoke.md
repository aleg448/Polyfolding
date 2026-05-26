# CrystalProbe Backend Smoke Benchmark

- Status: `backend_smoke_recorded_with_blockers`
- Backends: `mace, aimnet2`
- Selected inputs: `1`
- Backend rows: `2`
- Passed rows: `1`
- Blocked rows: `1`
- Failed rows: `0`
- Skipped rows: `0`
- Claim-ready rows: `0`
- Claim boundary: `backend_smoke_generated_conformer_not_scientific_evidence`

## Bug Signatures

| Signature | Severity | Count | Examples | Detail |
|---|---|---:|---|---|
| `backend_missing_windows_cpp_compiler` | `blocked` | `1` | aimnet2:water | InductorError: RuntimeError: Compiler: cl is not found. Set TORCHDYNAMO_VERBOSE=1 for the internal stack trace (please do this especially if you're reporting a bug to PyTorch). For even more developer context, set TORCH_LOGS="+dynamo" |

## Backend Rows

| Molecule | Backend | Status | Energy eV | Max force | Runtime s | Signature | Detail |
|---|---|---|---:|---:|---:|---|---|
| `water` | `mace` | `passed` | `-2081.07` | `1.70648` | `8.79113` | `none` | Backend smoke prediction completed on generated conformer input. |
| `water` | `aimnet2` | `blocked` | `` | `` | `8.73432` | `backend_missing_windows_cpp_compiler` | InductorError: RuntimeError: Compiler: cl is not found. Set TORCHDYNAMO_VERBOSE=1 for the internal stack trace (please do this especially if you're reporting a bug to PyTorch). For even more developer context, set TORCH_LOGS="+dynamo" |

## Policy

- Backend smoke rows prove only that a backend can execute on a generated local input.
- Absolute energies from different backends are not commensurate benchmark claims.
- Generated conformer smoke results must stay below verified drug-discovery or stability claims.
- Blocked backend rows are useful engineering evidence and should be fixed before larger benchmarks.
