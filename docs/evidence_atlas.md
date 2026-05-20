# CrystalProbe Evidence Atlas

- Status: `evidence_atlas_built`
- SQLite database: `outputs/crystalprobe_evidence_atlas.sqlite`
- Static explorer: [evidence_atlas.html](evidence_atlas.html)

## Counts

| Table | Rows |
|---|---:|
| `molecules` | `5` |
| `polymorph_pairs` | `5` |
| `structures` | `12` |
| `evidence_sources` | `3` |
| `claim_gates` | `5` |
| `blockers` | `17` |
| `viewer_links` | `2` |
| `predictions` | `2` |
| `artifacts` | `253` |

## Claim Status

| Status | Pairs |
|---|---:|
| `draft` | `5` |

## Query Examples

```sql
select pair_id, curation_status, blocker_count from polymorph_pairs order by blocker_count desc;
select pair_id, source_id, viewer_url from viewer_links where claim_label = 'candidate_unverified';
select path, category from artifacts where category != 'candidate_public';
```

## Highlighted Records

| Pair | Molecule | Status | Blockers | Viewers | Promotion |
|---|---|---|---:|---:|---|
| `aspirin_form_i_vs_form_ii_seed` | aspirin | `draft` | `1` | `0` | `not_recorded` |
| `paracetamol_form_i_vs_form_ii_seed` | paracetamol | `draft` | `2` | `2` | `do_not_promote_candidate_only` |
| `glycine_alpha_vs_gamma_seed` | glycine | `draft` | `1` | `0` | `not_recorded` |
| `carbamazepine_form_i_vs_form_iii_seed` | carbamazepine | `draft` | `1` | `0` | `not_recorded` |
| `urea_form_i_vs_form_ii_seed` | urea | `draft` | `1` | `0` | `not_recorded` |

## Policy

- The atlas is a query layer over existing CrystalProbe artifacts; it does not promote records.
- Only verified records with unambiguous evidence may support headline benchmark claims.
- Candidate viewer links are navigation aids and do not embed atom coordinates or CIF text.
- Release-boundary categories must be reviewed before public sharing of generated artifacts.
