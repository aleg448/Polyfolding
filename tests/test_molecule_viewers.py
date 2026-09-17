import json
from pathlib import Path

from crystalprobe.insight.molecule_viewers import (
    _structure_card,
    molecule_viewer_html,
    molecule_viewer_markdown,
    molecule_viewer_report,
)


ROOT = Path(__file__).resolve().parents[1]


def _viewer_report():
    candidates = json.loads(
        (ROOT / "data" / "curation" / "evidence_resolution_candidates_v0.1.json").read_text(encoding="utf-8")
    )
    return molecule_viewer_report(candidates)


def test_molecule_viewer_report_builds_candidate_safe_cod_targets():
    report = _viewer_report()

    assert report["status"] == "molecule_viewers_recorded"
    assert report["target_count"] == 1
    assert report["structure_viewer_count"] == 2
    target = report["targets"][0]
    assert target["pair_id"] == "paracetamol_form_i_vs_form_ii_seed"
    by_side = {structure["side"]: structure for structure in target["structures"]}
    assert by_side["A"]["source_id"] == "COD:7105573"
    assert by_side["B"]["source_id"] == "COD:2105052"
    assert {structure["claim_label"] for structure in target["structures"]} == {"candidate_unverified"}
    assert {structure["coordinates_embedded"] for structure in target["structures"]} == {False}
    assert {structure["coordinate_policy"] for structure in target["structures"]} == {
        "remote_source_only_no_coordinates_embedded"
    }


def test_molecule_viewer_markdown_and_html_keep_external_viewer_boundary_visible():
    report = _viewer_report()
    viewer_pages = {"paracetamol_form_i_vs_form_ii_seed": "docs/viewers/paracetamol_form_i_vs_form_ii_seed.html"}
    markdown = molecule_viewer_markdown(report, viewer_pages=viewer_pages)
    html = molecule_viewer_html(report, pair_id="paracetamol_form_i_vs_form_ii_seed")

    assert "Open COD JSmol" in markdown
    assert "candidate_unverified" in markdown
    assert "remote_source_only_no_coordinates_embedded" in markdown
    assert "https://www.crystallography.net/cod/7105573.html" in html
    assert "https://www.crystallography.net/cod/2105052.html" in html
    assert "candidate_unverified" in html
    assert "<iframe" in html
    assert "_atom_site" not in html


def _card_structure(**overrides):
    structure = {
        "side": "A",
        "proposed_form_label": "Form I",
        "source_database": "COD",
        "source_id": "COD:1",
        "viewer_url": "https://www.crystallography.net/cod/1.html",
        "cif_url": None,
        "space_group": "P 21/c",
        "license": "CC0-1.0",
        "has_disorder": False,
        "viewer_kind": "cod_jsmol_remote_page",
        "coordinate_policy": "remote_source_only_no_coordinates_embedded",
        "claim_label": "candidate_unverified",
        "coordinates_embedded": False,
    }
    structure.update(overrides)
    return structure


def test_structure_card_drops_javascript_scheme_urls():
    card = _structure_card(
        _card_structure(
            viewer_url="javascript:alert(1)",
            cif_url="javascript:alert(2)",
        )
    )
    assert "javascript:" not in card
    assert "<iframe" not in card  # unsafe URL must not auto-load in an iframe
    assert "Open COD JSmol" not in card
    assert "Open CIF Source" not in card
    assert "Viewer URL omitted" in card


def test_structure_card_keeps_safe_http_urls():
    card = _structure_card(_card_structure(cif_url="https://example.org/1.cif"))
    assert 'href="https://www.crystallography.net/cod/1.html"' in card
    assert "<iframe" in card
    assert 'href="https://example.org/1.cif"' in card
