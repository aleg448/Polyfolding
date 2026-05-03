from tests.test_schema import _record

from crystalprobe.benchmark.metrics import PairEnergyPrediction
from crystalprobe.benchmark.schema import PolymorphPair
from crystalprobe.insight.fingerprint import build_fingerprint_report
from crystalprobe.insight.reporting import fingerprint_markdown


def test_fingerprint_slices_by_tag_and_fields():
    record = _record()
    record["pair_id"] = "fixture"
    record["evidence"]["stability_ordering"] = "A>B"
    record["evidence"]["citation_doi"] = "10.0000/example"
    record["evidence"]["notes"] = ""
    pair = PolymorphPair.model_validate(record)
    report = build_fingerprint_report([pair], {"fixture": PairEnergyPrediction(-1.0, 0.0)})
    assert report.overall.accuracy == 1.0
    assert report.by_tag[0].name == "fixture"
    assert "CrystalProbe Fingerprint Report" in fingerprint_markdown(report)

