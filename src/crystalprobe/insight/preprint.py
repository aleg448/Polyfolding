"""ChemRxiv-style draft generation from CrystalProbe reports."""

from __future__ import annotations

from typing import Any


def chemrxiv_preprint_draft(
    *,
    memo_text: str,
    readiness: dict[str, Any],
    sensitivity: dict[str, Any],
    cposs_bridge: dict[str, Any],
    bundle_manifest: dict[str, Any],
    therapeutic_contrast: dict[str, Any] | None = None,
) -> str:
    """Render a structured preprint draft from local CrystalProbe artifacts."""

    title = "CrystalProbe: a reproducible pilot workflow for trust-aware organic crystal MLIP diagnostics"
    abstract = _abstract(readiness, sensitivity, cposs_bridge, bundle_manifest)
    lines = [
        f"# {title}",
        "",
        "## Abstract",
        "",
        abstract,
        "",
        "## 1. Introduction",
        "",
        (
            "Foundation machine-learned interatomic potentials are becoming practical tools for organic "
            "crystal modelling, but users still need explicit evidence about when a prediction should be "
            "trusted. CrystalProbe is designed as an interpretability-first research suite for this trust "
            "layer. The long-term objective is a curated polymorph-pair benchmark, behavioural fingerprints "
            "of major MLIPs, calibrated uncertainty wrappers, and usability infrastructure for CSP workflows."
        ),
        "",
        (
            "This draft reports the current pilot rather than the full benchmark. The pilot target is AMPETP, "
            "CCDC 1102740, a medication-adjacent amphetamine dihydrogen phosphate crystal. AMPETP is used here "
            "as a reproducibility and diagnostics target, not as a polymorph-ranking benchmark and not as a "
            "proxy for lisdexamfetamine dimesylate. The current pilot evidence is AGI-assisted and not "
            "human-validated, so the manuscript keeps benchmark and stability claims out of scope."
        ),
        "",
        "## 2. Methods",
        "",
        "### 2.1 Source Handling",
        "",
        (
            "The AMPETP block is extracted from a local CCDC/CSD multi-CIF export. Raw CCDC files remain local "
            "and are not redistributed. CrystalProbe records derived metadata, measurements, figures, and hashes."
        ),
        "",
        "### 2.2 Backend Measurements",
        "",
        (
            "MACE-OFF23 small and AIMNet2 are run on the same ASE-readable periodic AMPETP structure. Each output "
            "records total energy, force summaries, backend metadata, and local bond/contact/force diagnostics."
        ),
        "",
        "### 2.3 Perturbation Sensitivity",
        "",
        (
            "CrystalProbe generates deterministic perturbation probes around the AMPETP reference structure, "
            "including coordinate-noise variants, cell-scaling variants, and a combined perturbation. These probes "
            "are generated sensitivity inputs, not experimentally observed structures."
        ),
        "",
        "### 2.4 CPOSS Bridge",
        "",
        (
            "Existing local CPOSS MACE summaries for ibuprofen and carbamazepine are summarized as a bridge from "
            "single-crystal diagnostics toward formula-unit-normalized within-family ranking. This bridge remains "
            "separate from curated experimental stability claims."
        ),
        "",
        "### 2.5 Therapeutic Contrast",
        "",
        (
            "The same deterministic perturbation protocol is applied to ibuprofen CCDC 774097 as a neutral "
            "therapeutic contrast. MACE, AIMNet2, and UMA contrast reports now use the same AMPETP-vs-ibuprofen "
            "perturbation protocol while preserving within-backend interpretation boundaries."
        ),
        "",
        "## 3. Results",
        "",
        "### 3.1 AMPETP Readiness",
        "",
        f"The automated readiness gate reports `{readiness['status']}` with `{readiness['passed']}` checks passed and `{readiness['failed']}` failed.",
        f"The AMPETP research bundle contains `{len(bundle_manifest['artifacts'])}` hashed artifacts and manifest digest `{bundle_manifest['manifest_sha256']}`.",
        "",
        "### 3.2 Sensitivity",
        "",
    ]
    lines.extend(_sensitivity_result_lines(sensitivity))
    lines.extend(
        [
            "",
            "### 3.3 CPOSS Bridge",
            "",
            _cposs_table(cposs_bridge),
            "",
        ]
    )
    if therapeutic_contrast:
        lines.extend(
            [
                "### 3.4 Therapeutic Sensitivity Contrast",
                "",
                _contrast_table(therapeutic_contrast),
                "",
            ]
        )
    lines.extend(
        [
            "## 4. Discussion",
            "",
            (
                "The AMPETP pilot demonstrates that CrystalProbe can produce a complete, auditable evidence trail "
                "for one real crystal structure: source extraction, multi-backend inference, local diagnostics, "
                "perturbation sensitivity, generated figures, hashed artifacts, and readiness checks. The strongest "
                "sensitivity response appears in the same coordinate-noise probe for MACE-OFF23, AIMNet2, and UMA, "
                "and all three backends attach short-contact and high-force diagnostics to that probe."
            ),
            "",
            (
                "The CPOSS bridge shows how the same reporting layer starts to scale to multi-structure families. "
                "However, the bridge report does not yet replace curated polymorph-pair records with experimental "
                "stability evidence. It is an engineering and analysis bridge, not the final benchmark."
            ),
            "",
            (
                "The ibuprofen contrast is an early failure-mode comparison. Under the shared perturbation grid, "
                "the same coordinate-noise probe gives the largest response for AMPETP and ibuprofen across the "
                "pilot backends, but only AMPETP adds a short-contact diagnostic flag. This kind of contrast is the "
                "intended substrate for the later behavioural fingerprint paper."
            ),
            "",
            "## 5. Limitations",
            "",
            "- AMPETP is a single crystal structure and does not support polymorph ranking claims by itself.",
            "- AMPETP is not lisdexamfetamine dimesylate.",
            "- The current pilot is AGI-assisted and not human-validated.",
            "- Cross-backend absolute energy differences are not calibrated thermodynamic uncertainties.",
            "- Generated perturbation structures are sensitivity probes, not experimentally observed forms.",
            "- CPOSS bridge rankings still require curated experimental stability labels before publication as benchmark results.",
            "",
            "## 6. Reproducibility",
            "",
            "- AMPETP case-study report: `outputs/ampetp_case_study_report.json` and `outputs/ampetp_case_study_report.md`.",
            "- AMPETP sensitivity summary: `outputs/ampetp_sensitivity_summary.json` and `outputs/ampetp_sensitivity_summary.md`.",
            "- AMPETP figures: `outputs/figures/`.",
            "- AMPETP research bundle: `outputs/ampetp_research_bundle_manifest.json` and `outputs/ampetp_research_bundle_manifest.md`.",
            "- AMPETP readiness report: `outputs/ampetp_readiness_report.json` and `outputs/ampetp_readiness_report.md`.",
            "- CPOSS bridge report: `outputs/cposs_mini_benchmark_report.json` and `outputs/cposs_mini_benchmark_report.md`.",
            "- Therapeutic contrast report: `outputs/therapeutic_sensitivity_contrast_mace.json` and `outputs/therapeutic_sensitivity_contrast_mace.md`.",
            "- Evidence-tier report: `outputs/crystalprobe_evidence_tiers.json` and `outputs/crystalprobe_evidence_tiers.md`.",
            "",
            "## 7. Source Memo",
            "",
            "The following memo section was used as the draft seed.",
            "",
            memo_text.strip(),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _abstract(
    readiness: dict[str, Any],
    sensitivity: dict[str, Any],
    cposs_bridge: dict[str, Any],
    bundle_manifest: dict[str, Any],
) -> str:
    backends = ", ".join(_backend_label(backend) for backend in sorted(sensitivity["backends"]))
    return (
        "Machine-learned interatomic potentials are increasingly used in organic crystal modelling, "
        "but practical workflows need reproducible diagnostics and explicit trust boundaries. We present "
        "the current CrystalProbe pilot on AMPETP, CCDC 1102740, a medication-adjacent amphetamine "
        "dihydrogen phosphate crystal. The local workflow extracts AMPETP from a CCDC multi-CIF export, "
        f"runs {backends} backend measurements, computes bond and force diagnostics, evaluates deterministic "
        "perturbation sensitivity, generates paper figures, and records a hashed artifact bundle. The readiness "
        f"gate reports {readiness['passed']} checks passed and {readiness['failed']} failed, with "
        f"{len(bundle_manifest['artifacts'])} artifacts in the bundle. A CPOSS bridge report summarizes "
        f"{cposs_bridge['structure_count']} structures across {cposs_bridge['family_count']} families, connecting "
        "the pilot to the larger polymorph-ranking roadmap while preserving guardrails around experimental "
        "stability claims."
    )


def _backend_label(backend: str) -> str:
    return {
        "mace": "MACE-OFF23 small",
        "aimnet2": "AIMNet2",
        "uma": "UMA",
    }.get(backend, backend)


def _sensitivity_result_lines(summary: dict[str, Any]) -> list[str]:
    lines: list[str] = [
        "| Backend | Max abs delta (eV) | Mean abs delta (eV) | Largest-response variant | Flags |",
        "|---|---:|---:|---|---|",
    ]
    for backend, data in sorted(summary["backends"].items()):
        variants = [row for row in data["variants"] if row["variant"] != summary["reference_variant"]]
        largest = max(variants, key=lambda row: abs(float(row["energy_delta_ev"])))
        lines.append(
            f"| {backend} | {float(data['max_abs_energy_delta_ev']):.6f} | "
            f"{float(data['mean_abs_energy_delta_ev']):.6f} | {largest['variant']} | "
            f"{', '.join(largest.get('diagnostic_flags', [])) or 'none'} |"
        )
    return lines


def _cposs_table(report: dict[str, Any]) -> str:
    lines = [
        "| Family | Structures | Lowest | Second gap (kJ/mol) | Span (kJ/mol) | Flagged fraction |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for family, data in sorted(report["families"].items()):
        lines.append(
            f"| {family} | {data['structure_count']} | {data['lowest_structure']} | "
            f"{float(data['second_gap_kj_mol']):.3f} | {float(data['energy_span_kj_mol']):.3f} | "
            f"{float(data['flagged_fraction']):.3f} |"
        )
    return "\n".join(lines)


def _contrast_table(report: dict[str, Any]) -> str:
    lines = [
        "| Target | Backend | Max abs delta (eV) | Mean abs delta (eV) | Largest-response variant | Flags |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in report["targets"]:
        lines.append(
            f"| {row['target']} | {row['backend']} | {float(row['max_abs_energy_delta_ev']):.6f} | "
            f"{float(row['mean_abs_energy_delta_ev']):.6f} | {row['largest_response_variant']} | "
            f"{', '.join(row['largest_response_flags']) or 'none'} |"
        )
    return "\n".join(lines)
