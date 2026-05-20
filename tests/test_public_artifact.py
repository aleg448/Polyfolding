from crystalprobe.insight.public_artifact import build_public_artifact


def test_public_artifact_builder_writes_gallery_and_assets(tmp_path):
    result = build_public_artifact(
        output_dir=tmp_path / "outputs" / "public_demo",
        gallery_path=tmp_path / "docs" / "public_demo.md",
        asset_dir=tmp_path / "docs" / "assets" / "public_demo",
        checklist_path=tmp_path / "docs" / "public_demo_checklist.md",
        case_output_path=tmp_path / "docs" / "cases" / "cposs_ibp_candidate.md",
        case_asset_dir=tmp_path / "docs" / "assets" / "public_cases",
        backend_smoke="never",
    )

    gallery = tmp_path / "docs" / "public_demo.md"
    checklist = tmp_path / "docs" / "public_demo_checklist.md"
    case_doc = tmp_path / "docs" / "cases" / "cposs_ibp_candidate.md"
    case_figure = tmp_path / "docs" / "assets" / "public_cases" / "ibp_ibp01_psicrys_vs_ibp06_psicrys_backend_summary.svg"
    energy = tmp_path / "docs" / "assets" / "public_demo" / "energy_uncertainty.svg"
    claim_gate = tmp_path / "docs" / "assets" / "public_demo" / "claim_gate.svg"

    assert result["gallery"] == str(gallery)
    assert gallery.exists()
    assert checklist.exists()
    assert case_doc.exists()
    assert case_figure.exists()
    assert energy.exists()
    assert claim_gate.exists()
    text = gallery.read_text(encoding="utf-8")
    assert "![Claim Gate](assets/public_demo/claim_gate.svg)" in text
    assert "docs/public_demo_checklist.md" in text
    assert "python scripts\\build_public_artifact.py" in text
    assert "draft/unverified" in energy.read_text(encoding="utf-8")
    assert "candidate_unverified" in case_doc.read_text(encoding="utf-8")
    assert "IBP01_PsiCrys" in case_figure.read_text(encoding="utf-8")
