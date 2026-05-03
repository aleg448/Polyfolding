"""Markdown report generation for benchmark analyses."""

from __future__ import annotations

from crystalprobe.insight.fingerprint import FingerprintReport, SliceResult


def fingerprint_markdown(report: FingerprintReport, *, title: str = "CrystalProbe Fingerprint Report") -> str:
    lines = [f"# {title}", "", "## Overall", "", _table([report.overall]), ""]
    sections = [
        ("By Chemistry Tag", report.by_tag),
        ("By Flexibility", report.by_flexibility),
        ("By Halogen Flag", report.by_halogen),
        ("By Charge Flag", report.by_charge),
    ]
    for heading, rows in sections:
        lines.extend([f"## {heading}", "", _table(rows), ""])
    return "\n".join(lines).rstrip() + "\n"


def _table(rows: list[SliceResult]) -> str:
    table = ["| Slice | Accuracy | Correct | Evaluated | Skipped |", "|---|---:|---:|---:|---:|"]
    if not rows:
        table.append("| none | n/a | 0 | 0 | 0 |")
        return "\n".join(table)
    for row in rows:
        accuracy = "n/a" if row.accuracy is None else f"{row.accuracy:.3f}"
        table.append(f"| {row.name} | {accuracy} | {row.correct} | {row.evaluated} | {row.skipped} |")
    return "\n".join(table)

