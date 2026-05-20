from crystalprobe.insight.free_energy_probe import (
    bennett_acceptance_delta_f,
    free_energy_probe_markdown,
    free_energy_probe_report,
    zwanzig_delta_f,
)


def test_zwanzig_recovers_constant_work():
    assert round(zwanzig_delta_f([5.0, 5.0, 5.0]), 6) == 5.0


def test_bennett_acceptance_recovers_symmetric_constant_work():
    assert round(bennett_acceptance_delta_f([5.0, 5.0, 5.0], [-5.0, -5.0, -5.0]), 3) == 5.0


def test_free_energy_probe_abstains_on_insufficient_samples():
    report = free_energy_probe_report([5.0], min_samples=3)

    assert report["status"] == "abstained_insufficient_forward_samples"
    assert report["forward_zwanzig_delta_f_kj_per_mol"] is None


def test_free_energy_probe_records_claim_boundary():
    report = free_energy_probe_report([4.9, 5.0, 5.1], reverse_work_kj_per_mol=[-5.0, -5.1, -4.9])
    markdown = free_energy_probe_markdown(report)

    assert report["status"] == "free_energy_probe_recorded"
    assert "method evidence until convergence" in markdown
