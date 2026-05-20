from crystalprobe.insight.landscape_audit import landscape_audit_markdown, landscape_audit_report


def test_landscape_audit_flags_backend_winner_disagreement():
    report = landscape_audit_report(
        [
            {"family_id": "ibp", "candidate_id": "a", "backend": "mace", "energy": -2.0, "fingerprint": "basin_a"},
            {"family_id": "ibp", "candidate_id": "b", "backend": "mace", "energy": -1.0, "fingerprint": "basin_b"},
            {"family_id": "ibp", "candidate_id": "a", "backend": "aimnet2", "energy": -1.0, "fingerprint": "basin_a"},
            {"family_id": "ibp", "candidate_id": "b", "backend": "aimnet2", "energy": -2.0, "fingerprint": "basin_b"},
        ]
    )

    assert report["status"] == "landscape_audit_review_required"
    assert report["backend_winner_disagreement_count"] == 1
    assert report["families"][0]["backend_winners"] == {"aimnet2": "b", "mace": "a"}


def test_landscape_audit_flags_duplicate_basins():
    report = landscape_audit_report(
        [
            {"family_id": "cbz", "candidate_id": "a", "backend": "mace", "energy": -2.0, "fingerprint": "same"},
            {"family_id": "cbz", "candidate_id": "b", "backend": "mace", "energy": -1.9, "fingerprint": "same"},
        ]
    )
    markdown = landscape_audit_markdown(report)

    assert report["duplicate_group_count"] == 1
    assert "Duplicate Groups" in markdown
