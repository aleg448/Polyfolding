"""Queryable evidence atlas for CrystalProbe records and artifacts."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records
from crystalprobe.benchmark.schema import PolymorphPair


TABLE_COLUMNS = {
    "molecules": [
        "molecule_id",
        "common_name",
        "smiles",
        "inchi",
        "cas_number",
        "flexibility_class",
        "functional_groups",
        "h_bond_motifs",
        "has_charge",
        "has_halogen",
        "is_chiral",
    ],
    "polymorph_pairs": [
        "pair_id",
        "molecule_id",
        "molecule_name",
        "curation_status",
        "stability_ordering",
        "experimental_winner",
        "headline_claim_gate",
        "candidate_status",
        "promotion_decision",
        "proposed_stability_ordering",
        "blocker_count",
        "viewer_count",
    ],
    "structures": [
        "structure_key",
        "pair_id",
        "side",
        "record_kind",
        "structure_id",
        "form_label",
        "source",
        "source_id",
        "license",
        "space_group",
        "cif_path",
        "cif_url",
        "viewer_url",
        "has_disorder",
        "coordinate_policy",
        "claim_label",
    ],
    "evidence_sources": [
        "source_key",
        "pair_id",
        "title",
        "doi",
        "url",
        "evidence_role",
        "evidence_note",
        "source_kind",
    ],
    "claim_gates": [
        "pair_id",
        "headline_claim_gate",
        "can_make_headline_claim",
        "curation_status",
        "blocker_count",
        "promotion_decision",
        "claim_scope",
    ],
    "blockers": [
        "blocker_key",
        "pair_id",
        "field",
        "severity",
        "message",
        "status",
        "candidate_value",
        "evidence",
    ],
    "viewer_links": [
        "viewer_key",
        "pair_id",
        "side",
        "source_id",
        "viewer_url",
        "cif_url",
        "viewer_kind",
        "claim_label",
        "coordinate_policy",
    ],
    "predictions": [
        "pair_id",
        "model_name",
        "model_version",
        "energy_a",
        "energy_b",
        "predicted_winner",
        "energy_gap_b_minus_a",
        "energy_uncertainty_a",
        "energy_uncertainty_b",
        "ood_flag_a",
        "ood_flag_b",
        "energy_unit",
        "notes",
        "claim_boundary",
    ],
    "artifacts": [
        "path",
        "category",
        "reason",
    ],
}


def build_evidence_atlas(
    *,
    manifest_path: str | Path,
    predictions_path: str | Path,
    evidence_packet: dict[str, Any] | None = None,
    evidence_resolution: dict[str, Any] | None = None,
    molecule_viewers: dict[str, Any] | None = None,
    release_boundary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a normalized evidence atlas from existing CrystalProbe artifacts."""

    dataset = load_manifest(manifest_path)
    prediction_records = load_pair_energy_prediction_records(predictions_path)
    evidence_packet = evidence_packet or {}
    evidence_resolution = evidence_resolution or {}
    molecule_viewers = molecule_viewers or {}
    release_boundary = release_boundary or {}

    viewer_structures = _viewer_structures_by_pair_side(molecule_viewers)
    resolution_by_pair = _single_or_empty(evidence_resolution)
    packet_by_pair = _single_or_empty(evidence_packet)

    molecules = _molecule_rows(dataset.pairs)
    structures = _canonical_structure_rows(dataset.pairs, viewer_structures)
    structures.extend(_candidate_structure_rows(molecule_viewers))
    evidence_sources = _evidence_source_rows(dataset.pairs, evidence_resolution)
    blockers = _blocker_rows(packet_by_pair, resolution_by_pair)
    viewer_links = _viewer_link_rows(molecule_viewers)
    predictions = _prediction_rows(prediction_records, dataset.pairs)
    artifacts = _artifact_rows(release_boundary)
    pairs = _pair_rows(dataset.pairs, resolution_by_pair, packet_by_pair, viewer_links)
    claim_gates = _claim_gate_rows(pairs)

    tables = {
        "molecules": molecules,
        "polymorph_pairs": pairs,
        "structures": structures,
        "evidence_sources": evidence_sources,
        "claim_gates": claim_gates,
        "blockers": blockers,
        "viewer_links": viewer_links,
        "predictions": predictions,
        "artifacts": artifacts,
    }
    counts = {name: len(rows) for name, rows in tables.items()}
    counts["candidate_public_artifacts"] = sum(1 for row in artifacts if row["category"] == "candidate_public")
    counts["license_review_required_artifacts"] = sum(
        1 for row in artifacts if row["category"] == "license_review_required"
    )
    counts["local_only_artifacts"] = sum(1 for row in artifacts if row["category"] == "local_only")
    status_counts = Counter(row["curation_status"] for row in pairs)
    return {
        "schema_version": "0.1.0",
        "status": "evidence_atlas_built",
        "inputs": {
            "manifest": str(manifest_path),
            "predictions": str(predictions_path),
        },
        "counts": counts,
        "curation_status_counts": dict(sorted(status_counts.items())),
        "tables": tables,
        "policy": [
            "The atlas is a query layer over existing CrystalProbe artifacts; it does not promote records.",
            "Only verified records with unambiguous evidence may support headline benchmark claims.",
            "Candidate viewer links are navigation aids and do not embed atom coordinates or CIF text.",
            "Release-boundary categories must be reviewed before public sharing of generated artifacts.",
        ],
    }


def write_evidence_atlas_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write the evidence atlas to a small SQLite database."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for table, columns in TABLE_COLUMNS.items():
            column_defs = ", ".join(f"{column} TEXT" for column in columns)
            connection.execute(f"CREATE TABLE {table} ({column_defs})")
            rows = report["tables"].get(table, [])
            if not rows:
                continue
            placeholders = ", ".join("?" for _ in columns)
            connection.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                [_sqlite_row(row, columns) for row in rows],
            )
        connection.execute("CREATE INDEX idx_pairs_status ON polymorph_pairs(curation_status)")
        connection.execute("CREATE INDEX idx_structures_pair ON structures(pair_id)")
        connection.execute("CREATE INDEX idx_blockers_pair ON blockers(pair_id)")
        connection.execute("CREATE INDEX idx_artifacts_category ON artifacts(category)")


def evidence_atlas_markdown(report: dict[str, Any], *, sqlite_path: str, explorer_path: str) -> str:
    """Render a concise atlas summary as Markdown."""

    counts = report["counts"]
    lines = [
        "# CrystalProbe Evidence Atlas",
        "",
        f"- Status: `{report['status']}`",
        f"- SQLite database: `{sqlite_path}`",
        f"- Static explorer: [{explorer_path}]({explorer_path})",
        "",
        "## Counts",
        "",
        "| Table | Rows |",
        "|---|---:|",
    ]
    for table in TABLE_COLUMNS:
        lines.append(f"| `{table}` | `{counts.get(table, 0)}` |")
    lines.extend(
        [
            "",
            "## Claim Status",
            "",
            "| Status | Pairs |",
            "|---|---:|",
        ]
    )
    for status, count in report.get("curation_status_counts", {}).items():
        lines.append(f"| `{status}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Query Examples",
            "",
            "```sql",
            "select pair_id, curation_status, blocker_count from polymorph_pairs order by blocker_count desc;",
            "select pair_id, source_id, viewer_url from viewer_links where claim_label = 'candidate_unverified';",
            "select path, category from artifacts where category != 'candidate_public';",
            "```",
            "",
            "## Highlighted Records",
            "",
            "| Pair | Molecule | Status | Blockers | Viewers | Promotion |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    for row in report["tables"]["polymorph_pairs"]:
        lines.append(
            f"| `{row['pair_id']}` | {row['molecule_name']} | `{row['curation_status']}` | "
            f"`{row['blocker_count']}` | `{row['viewer_count']}` | `{row['promotion_decision']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report.get("policy", []))
    return "\n".join(lines).rstrip() + "\n"


def evidence_atlas_explorer_html(report: dict[str, Any]) -> str:
    """Render a self-contained static explorer for the evidence atlas."""

    payload = _json_script_payload(_explorer_payload(report))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CrystalProbe Evidence Atlas</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18212f;
      --muted: #627084;
      --line: #d8e0ea;
      --panel: #f6f8fb;
      --accent: #0b7285;
      --accent-soft: #e7f6f8;
      --warn: #9a5b00;
      --warn-soft: #fff6df;
      --ok: #286245;
      --bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.42;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    .wrap {{
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
    }}
    .top {{
      padding: 26px 0 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 29px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subhead {{
      margin: 0;
      max-width: 900px;
      color: var(--muted);
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
      gap: 10px;
      padding: 14px 0 18px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 11px 12px;
      background: var(--panel);
    }}
    .metric strong {{
      display: block;
      font-size: 22px;
      line-height: 1.1;
    }}
    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(300px, 420px) 1fr;
      gap: 18px;
      padding: 20px 0 36px;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      margin-bottom: 12px;
    }}
    input, select {{
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 10px;
      font: inherit;
      background: #fff;
    }}
    .pair-list {{
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .pair-button {{
      width: 100%;
      display: grid;
      gap: 4px;
      padding: 12px 13px;
      border: 0;
      border-bottom: 1px solid var(--line);
      background: #fff;
      text-align: left;
      color: var(--ink);
      cursor: pointer;
    }}
    .pair-button:last-child {{ border-bottom: 0; }}
    .pair-button.active {{
      background: var(--accent-soft);
      box-shadow: inset 3px 0 0 var(--accent);
    }}
    .pair-title {{
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .pair-meta {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 13px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      font-size: 12px;
      font-weight: 650;
    }}
    .badge.warn {{
      color: var(--warn);
      border-color: #efcf88;
      background: var(--warn-soft);
    }}
    .badge.ok {{
      color: var(--ok);
      border-color: #a9d6bf;
      background: #ecfbf2;
    }}
    .detail {{
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: 560px;
      overflow: hidden;
    }}
    .detail-head {{
      padding: 16px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    .detail-head h2 {{
      margin: 0 0 8px;
      font-size: 22px;
      line-height: 1.15;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }}
    .detail-body {{
      padding: 16px;
      display: grid;
      gap: 18px;
    }}
    section h3 {{
      margin: 0 0 8px;
      font-size: 16px;
      letter-spacing: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 7px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
      background: #fafbfc;
    }}
    td {{
      overflow-wrap: anywhere;
    }}
    a {{ color: var(--accent); }}
    .empty {{
      color: var(--muted);
      padding: 10px 0;
    }}
    .policy {{
      margin-top: 4px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 12px 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 840px) {{
      main {{ grid-template-columns: 1fr; }}
      .toolbar {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap top">
      <h1>CrystalProbe Evidence Atlas</h1>
      <p class="subhead">A queryable, claim-gated database view of molecules, polymorph pairs, source candidates, predictions, blockers, viewer links, and release-boundary artifacts.</p>
      <div class="summary" id="summary"></div>
    </div>
  </header>
  <main class="wrap">
    <aside>
      <div class="toolbar">
        <input id="search" type="search" placeholder="Search molecules, pairs, sources">
        <select id="statusFilter" aria-label="Filter by curation status">
          <option value="">All statuses</option>
        </select>
      </div>
      <div class="pair-list" id="pairList"></div>
    </aside>
    <article class="detail" id="detail"></article>
  </main>
  <script id="atlas-data" type="application/json">{payload}</script>
  <script>
    const atlas = JSON.parse(document.getElementById('atlas-data').textContent);
    const state = {{ selected: atlas.pairs[0]?.pair_id || null }};
    const search = document.getElementById('search');
    const statusFilter = document.getElementById('statusFilter');
    const pairList = document.getElementById('pairList');
    const detail = document.getElementById('detail');
    const summary = document.getElementById('summary');

    function esc(value) {{
      return String(value ?? '').replace(/[&<>"']/g, ch => ({{
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }}[ch]));
    }}
    function badge(value, kind = '') {{
      return `<span class="badge ${{kind}}">${{esc(value)}}</span>`;
    }}
    function link(url, label) {{
      if (!url) return '';
      return `<a href="${{esc(url)}}" target="_blank" rel="noopener noreferrer">${{esc(label)}}</a>`;
    }}
    function rows(items, columns) {{
      if (!items.length) return '<div class="empty">No rows recorded.</div>';
      const head = columns.map(col => `<th>${{esc(col.label)}}</th>`).join('');
      const body = items.map(item => `<tr>${{columns.map(col => `<td>${{col.render(item)}}</td>`).join('')}}</tr>`).join('');
      return `<table><thead><tr>${{head}}</tr></thead><tbody>${{body}}</tbody></table>`;
    }}
    function filteredPairs() {{
      const q = search.value.trim().toLowerCase();
      const status = statusFilter.value;
      return atlas.pairs.filter(pair => {{
        const haystack = [pair.pair_id, pair.molecule_name, pair.curation_status, pair.promotion_decision]
          .concat((atlas.structures[pair.pair_id] || []).map(row => row.source_id))
          .join(' ').toLowerCase();
        return (!status || pair.curation_status === status) && (!q || haystack.includes(q));
      }});
    }}
    function renderSummary() {{
      const metrics = [
        ['Molecules', atlas.counts.molecules],
        ['Pairs', atlas.counts.polymorph_pairs],
        ['Structures', atlas.counts.structures],
        ['Evidence sources', atlas.counts.evidence_sources],
        ['Viewer links', atlas.counts.viewer_links],
        ['Artifacts', atlas.counts.artifacts]
      ];
      summary.innerHTML = metrics.map(([label, value]) => `<div class="metric"><strong>${{esc(value)}}</strong><span>${{esc(label)}}</span></div>`).join('');
      const statuses = [...new Set(atlas.pairs.map(pair => pair.curation_status))].sort();
      statusFilter.innerHTML = '<option value="">All statuses</option>' + statuses.map(status => `<option value="${{esc(status)}}">${{esc(status)}}</option>`).join('');
    }}
    function renderList() {{
      const pairs = filteredPairs();
      if (!pairs.some(pair => pair.pair_id === state.selected)) {{
        state.selected = pairs[0]?.pair_id || null;
      }}
      pairList.innerHTML = pairs.map(pair => {{
        const active = pair.pair_id === state.selected ? ' active' : '';
        const claimKind = pair.headline_claim_gate.includes('blocked') ? 'warn' : 'ok';
        return `<button class="pair-button${{active}}" data-pair="${{esc(pair.pair_id)}}"><span class="pair-title">${{esc(pair.molecule_name)}}</span><span>${{esc(pair.pair_id)}}</span><span class="pair-meta">${{badge(pair.curation_status)}}${{badge(pair.headline_claim_gate, claimKind)}}${{badge(pair.blocker_count + ' blockers', pair.blocker_count > 0 ? 'warn' : 'ok')}}</span></button>`;
      }}).join('') || '<div class="empty">No matching pairs.</div>';
      pairList.querySelectorAll('button[data-pair]').forEach(button => {{
        button.addEventListener('click', () => {{
          state.selected = button.dataset.pair;
          renderList();
          renderDetail();
        }});
      }});
    }}
    function renderDetail() {{
      const pair = atlas.pairs.find(row => row.pair_id === state.selected);
      if (!pair) {{
        detail.innerHTML = '<div class="detail-body"><div class="empty">No pair selected.</div></div>';
        return;
      }}
      const structures = atlas.structures[pair.pair_id] || [];
      const blockers = atlas.blockers[pair.pair_id] || [];
      const evidence = atlas.evidence_sources[pair.pair_id] || [];
      const viewers = atlas.viewer_links[pair.pair_id] || [];
      const predictions = atlas.predictions[pair.pair_id] || [];
      detail.innerHTML = `
        <div class="detail-head">
          <h2>${{esc(pair.molecule_name)}} · ${{esc(pair.pair_id)}}</h2>
          <div class="pair-meta">
            ${{badge(pair.curation_status)}}
            ${{badge(pair.headline_claim_gate, pair.headline_claim_gate.includes('blocked') ? 'warn' : 'ok')}}
            ${{badge('promotion: ' + pair.promotion_decision, pair.promotion_decision.includes('do_not') ? 'warn' : '')}}
            ${{badge('viewers: ' + pair.viewer_count)}}
          </div>
        </div>
        <div class="detail-body">
          <section>
            <h3>Structures</h3>
            ${{rows(structures, [
              {{label: 'Side', render: row => esc(row.side)}},
              {{label: 'Kind', render: row => esc(row.record_kind)}},
              {{label: 'Form', render: row => esc(row.form_label)}},
              {{label: 'Source', render: row => esc(row.source_id)}},
              {{label: 'License', render: row => esc(row.license)}},
              {{label: 'Viewer', render: row => link(row.viewer_url, 'open')}}
            ])}}
          </section>
          <section>
            <h3>Evidence Sources</h3>
            ${{rows(evidence, [
              {{label: 'Role', render: row => esc(row.evidence_role || row.source_kind)}},
              {{label: 'Title', render: row => esc(row.title)}},
              {{label: 'DOI', render: row => esc(row.doi)}},
              {{label: 'URL', render: row => link(row.url, 'source')}}
            ])}}
          </section>
          <section>
            <h3>Blockers</h3>
            ${{rows(blockers, [
              {{label: 'Status', render: row => esc(row.status)}},
              {{label: 'Field', render: row => esc(row.field)}},
              {{label: 'Message', render: row => esc(row.message || row.evidence)}},
              {{label: 'Candidate Value', render: row => esc(row.candidate_value)}}
            ])}}
          </section>
          <section>
            <h3>Predictions</h3>
            ${{rows(predictions, [
              {{label: 'Model', render: row => esc(row.model_name)}},
              {{label: 'Winner', render: row => esc(row.predicted_winner)}},
              {{label: 'Gap B-A', render: row => esc(row.energy_gap_b_minus_a)}},
              {{label: 'OOD', render: row => esc(row.ood_flag_a || row.ood_flag_b)}},
              {{label: 'Boundary', render: row => esc(row.claim_boundary)}}
            ])}}
          </section>
          <section>
            <h3>Viewer Links</h3>
            ${{rows(viewers, [
              {{label: 'Side', render: row => esc(row.side)}},
              {{label: 'Source', render: row => esc(row.source_id)}},
              {{label: 'Label', render: row => esc(row.claim_label)}},
              {{label: 'Viewer', render: row => link(row.viewer_url, 'COD/JSmol')}},
              {{label: 'Policy', render: row => esc(row.coordinate_policy)}}
            ])}}
          </section>
          <div class="policy">${{atlas.policy.map(line => `<div>${{esc(line)}}</div>`).join('')}}</div>
        </div>`;
    }}
    search.addEventListener('input', () => {{ renderList(); renderDetail(); }});
    statusFilter.addEventListener('change', () => {{ renderList(); renderDetail(); }});
    renderSummary();
    renderList();
    renderDetail();
  </script>
</body>
</html>
"""


def _molecule_rows(pairs: Iterable[PolymorphPair]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for pair in pairs:
        molecule = pair.molecule
        molecule_id = _molecule_id(pair)
        rows[molecule_id] = {
            "molecule_id": molecule_id,
            "common_name": molecule.common_name or molecule.smiles,
            "smiles": molecule.smiles,
            "inchi": molecule.inchi,
            "cas_number": molecule.cas_number,
            "flexibility_class": molecule.flexibility_class,
            "functional_groups": "; ".join(molecule.functional_groups),
            "h_bond_motifs": "; ".join(molecule.h_bond_motifs),
            "has_charge": molecule.has_charge,
            "has_halogen": molecule.has_halogen,
            "is_chiral": molecule.is_chiral,
        }
    return sorted(rows.values(), key=lambda row: row["molecule_id"])


def _pair_rows(
    pairs: Iterable[PolymorphPair],
    resolution_by_pair: dict[str, dict[str, Any]],
    packet_by_pair: dict[str, dict[str, Any]],
    viewer_links: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    viewer_counts = Counter(row["pair_id"] for row in viewer_links)
    rows = []
    for pair in pairs:
        resolution = resolution_by_pair.get(pair.pair_id, {})
        packet = packet_by_pair.get(pair.pair_id, {})
        blocker_count = _blocker_count(pair, packet, resolution)
        rows.append(
            {
                "pair_id": pair.pair_id,
                "molecule_id": _molecule_id(pair),
                "molecule_name": pair.molecule.common_name or pair.molecule.smiles,
                "curation_status": pair.curation_status.value,
                "stability_ordering": pair.evidence.stability_ordering,
                "experimental_winner": pair.experimental_winner,
                "headline_claim_gate": _headline_claim_gate(pair),
                "candidate_status": resolution.get("candidate_status", "not_recorded"),
                "promotion_decision": resolution.get("promotion_decision", "not_recorded"),
                "proposed_stability_ordering": resolution.get("proposed_stability_ordering", "not_recorded"),
                "blocker_count": blocker_count,
                "viewer_count": viewer_counts.get(pair.pair_id, 0),
            }
        )
    return rows


def _canonical_structure_rows(
    pairs: Iterable[PolymorphPair],
    viewer_structures: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        for side, structure in (("A", pair.structure_a), ("B", pair.structure_b)):
            viewer = viewer_structures.get((pair.pair_id, side), {})
            rows.append(
                {
                    "structure_key": f"{pair.pair_id}:{side}:manifest",
                    "pair_id": pair.pair_id,
                    "side": side,
                    "record_kind": "canonical_manifest",
                    "structure_id": structure.structure_id,
                    "form_label": structure.label,
                    "source": structure.source.value,
                    "source_id": structure.source_id,
                    "license": structure.license,
                    "space_group": structure.space_group,
                    "cif_path": structure.cif_path,
                    "cif_url": None,
                    "viewer_url": viewer.get("viewer_url"),
                    "has_disorder": pair.has_disorder,
                    "coordinate_policy": "manifest_reference_no_coordinates_embedded",
                    "claim_label": f"{pair.curation_status.value}_unverified"
                    if pair.curation_status.value != "verified"
                    else "verified",
                }
            )
    return rows


def _candidate_structure_rows(molecule_viewers: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in molecule_viewers.get("targets", []):
        pair_id = target["pair_id"]
        for structure in target.get("structures", []):
            side = structure["side"]
            rows.append(
                {
                    "structure_key": f"{pair_id}:{side}:candidate_source",
                    "pair_id": pair_id,
                    "side": side,
                    "record_kind": "candidate_source",
                    "structure_id": structure.get("source_id"),
                    "form_label": structure.get("proposed_form_label"),
                    "source": structure.get("source_database"),
                    "source_id": structure.get("source_id"),
                    "license": structure.get("license"),
                    "space_group": structure.get("space_group"),
                    "cif_path": None,
                    "cif_url": structure.get("cif_url"),
                    "viewer_url": structure.get("viewer_url"),
                    "has_disorder": structure.get("has_disorder"),
                    "coordinate_policy": structure.get("coordinate_policy"),
                    "claim_label": structure.get("claim_label", "candidate_unverified"),
                }
            )
    return rows


def _evidence_source_rows(pairs: Iterable[PolymorphPair], evidence_resolution: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        if pair.evidence.citation_doi or pair.evidence.citation_url:
            rows.append(
                {
                    "source_key": f"{pair.pair_id}:manifest_evidence",
                    "pair_id": pair.pair_id,
                    "title": "Manifest experimental evidence",
                    "doi": pair.evidence.citation_doi,
                    "url": pair.evidence.citation_url,
                    "evidence_role": "manifest_stability_evidence",
                    "evidence_note": pair.evidence.notes,
                    "source_kind": "manifest",
                }
            )
    if evidence_resolution.get("pair_id"):
        pair_id = evidence_resolution["pair_id"]
        for index, source in enumerate(evidence_resolution.get("stability_sources", []), start=1):
            rows.append(
                {
                    "source_key": f"{pair_id}:candidate:{index}",
                    "pair_id": pair_id,
                    "title": source.get("title"),
                    "doi": source.get("doi"),
                    "url": source.get("url"),
                    "evidence_role": source.get("evidence_role"),
                    "evidence_note": source.get("evidence_note"),
                    "source_kind": "candidate_resolution",
                }
            )
    return rows


def _blocker_rows(
    packet_by_pair: dict[str, dict[str, Any]],
    resolution_by_pair: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for pair_id, packet in packet_by_pair.items():
        for index, blocker in enumerate((packet.get("promotion_gate") or {}).get("blockers", []), start=1):
            rows.append(
                {
                    "blocker_key": f"{pair_id}:open:{index}",
                    "pair_id": pair_id,
                    "field": blocker.get("field"),
                    "severity": blocker.get("severity", "blocker"),
                    "message": blocker.get("message"),
                    "status": "open_in_packet",
                    "candidate_value": None,
                    "evidence": None,
                }
            )
    for pair_id, resolution in resolution_by_pair.items():
        for index, blocker in enumerate(resolution.get("resolved_blockers", []), start=1):
            rows.append(
                {
                    "blocker_key": f"{pair_id}:candidate_resolved:{index}",
                    "pair_id": pair_id,
                    "field": blocker.get("field"),
                    "severity": "candidate_resolution",
                    "message": None,
                    "status": "candidate_resolved_not_promoted",
                    "candidate_value": blocker.get("candidate_value"),
                    "evidence": blocker.get("evidence"),
                }
            )
        for index, blocker in enumerate(resolution.get("remaining_blockers", []), start=1):
            rows.append(
                {
                    "blocker_key": f"{pair_id}:remaining:{index}",
                    "pair_id": pair_id,
                    "field": blocker.get("field"),
                    "severity": blocker.get("severity", "blocker"),
                    "message": blocker.get("message"),
                    "status": "remaining_after_candidate_resolution",
                    "candidate_value": None,
                    "evidence": None,
                }
            )
    return rows


def _viewer_link_rows(molecule_viewers: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in molecule_viewers.get("targets", []):
        pair_id = target["pair_id"]
        for structure in target.get("structures", []):
            side = structure["side"]
            rows.append(
                {
                    "viewer_key": f"{pair_id}:{side}:{structure.get('source_id')}",
                    "pair_id": pair_id,
                    "side": side,
                    "source_id": structure.get("source_id"),
                    "viewer_url": structure.get("viewer_url"),
                    "cif_url": structure.get("cif_url"),
                    "viewer_kind": structure.get("viewer_kind"),
                    "claim_label": structure.get("claim_label"),
                    "coordinate_policy": structure.get("coordinate_policy"),
                }
            )
    return rows


def _prediction_rows(records: Iterable[Any], pairs: list[PolymorphPair]) -> list[dict[str, Any]]:
    pair_by_id = {pair.pair_id: pair for pair in pairs}
    rows = []
    for record in records:
        pair = pair_by_id.get(record.pair_id)
        rows.append(
            {
                "pair_id": record.pair_id,
                "model_name": record.model_name,
                "model_version": record.model_version,
                "energy_a": record.energy_a,
                "energy_b": record.energy_b,
                "predicted_winner": record.as_metric_prediction().predicted_winner,
                "energy_gap_b_minus_a": record.energy_b - record.energy_a,
                "energy_uncertainty_a": record.energy_uncertainty_a,
                "energy_uncertainty_b": record.energy_uncertainty_b,
                "ood_flag_a": record.ood_flag_a,
                "ood_flag_b": record.ood_flag_b,
                "energy_unit": record.energy_unit,
                "notes": record.notes,
                "claim_boundary": _prediction_claim_boundary(pair),
            }
        )
    return rows


def _artifact_rows(release_boundary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": record.get("path"),
            "category": record.get("category"),
            "reason": record.get("reason"),
        }
        for record in release_boundary.get("records", [])
    ]


def _claim_gate_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for pair in pair_rows:
        allowed = pair["headline_claim_gate"] == "verified_only_claims_allowed"
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "headline_claim_gate": pair["headline_claim_gate"],
                "can_make_headline_claim": allowed,
                "curation_status": pair["curation_status"],
                "blocker_count": pair["blocker_count"],
                "promotion_decision": pair["promotion_decision"],
                "claim_scope": "verified benchmark slice" if allowed else "workflow, curation, or candidate evidence only",
            }
        )
    return rows


def _explorer_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "counts": report["counts"],
        "policy": report["policy"],
        "pairs": report["tables"]["polymorph_pairs"],
        "structures": _group_by_pair(report["tables"]["structures"]),
        "evidence_sources": _group_by_pair(report["tables"]["evidence_sources"]),
        "blockers": _group_by_pair(report["tables"]["blockers"]),
        "viewer_links": _group_by_pair(report["tables"]["viewer_links"]),
        "predictions": _group_by_pair(report["tables"]["predictions"]),
    }


def _group_by_pair(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("pair_id")), []).append(row)
    return grouped


def _viewer_structures_by_pair_side(molecule_viewers: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows = {}
    for target in molecule_viewers.get("targets", []):
        for structure in target.get("structures", []):
            rows[(target["pair_id"], structure["side"])] = structure
    return rows


def _single_or_empty(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pair_id = report.get("pair_id")
    return {pair_id: report} if pair_id else {}


def _molecule_id(pair: PolymorphPair) -> str:
    return (pair.molecule.common_name or pair.molecule.smiles).lower().replace(" ", "_")


def _headline_claim_gate(pair: PolymorphPair) -> str:
    if pair.curation_status.value == "verified" and pair.experimental_winner:
        return "verified_only_claims_allowed"
    return "blocked_until_verified"


def _blocker_count(pair: PolymorphPair, packet: dict[str, Any], resolution: dict[str, Any]) -> int:
    if resolution:
        return int(resolution.get("remaining_blocker_count", 0))
    if packet:
        return int((packet.get("promotion_gate") or {}).get("blocker_count", 0))
    if pair.curation_status.value == "verified":
        return 0
    return 1


def _prediction_claim_boundary(pair: PolymorphPair | None) -> str:
    if pair is None:
        return "prediction has no matching manifest record"
    if pair.curation_status.value == "verified":
        return "may support verified-only scoring if release-boundary checks pass"
    return "demo signal only; record is not verified"


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[Any, ...]:
    values = []
    for column in columns:
        value = row.get(column)
        if isinstance(value, bool):
            values.append("true" if value else "false")
        elif value is None:
            values.append(None)
        elif isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append(str(value))
    return tuple(values)


def _json_script_payload(payload: dict[str, Any]) -> str:
    return (
        json.dumps(payload, sort_keys=True)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
