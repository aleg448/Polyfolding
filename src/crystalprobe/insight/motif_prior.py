"""Dependency-light motif priors for polymorph-pair triage."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


MOTIF_RULES: dict[str, dict[str, Any]] = {
    "amide": {"donors": 1, "acceptors": 1, "signals": ["amide_h_bond_competition"]},
    "amide_like": {"donors": 1, "acceptors": 1, "signals": ["amide_like_network"]},
    "amino_acid": {"donors": 1, "acceptors": 2, "signals": ["zwitterionic_packing"]},
    "amine": {"donors": 1, "acceptors": 1, "signals": ["amine_h_bonding"]},
    "carboxylate": {"donors": 0, "acceptors": 2, "signals": ["charge_assisted_h_bonding"]},
    "carboxylic_acid": {"donors": 1, "acceptors": 2, "signals": ["acid_dimer_or_chain"]},
    "ester": {"donors": 0, "acceptors": 2, "signals": ["acceptor_only_contacts"]},
    "phenol": {"donors": 1, "acceptors": 1, "signals": ["phenol_h_bonding"]},
    "urea": {"donors": 2, "acceptors": 1, "signals": ["bifurcated_h_bonding"]},
    "zwitterion": {"donors": 1, "acceptors": 2, "signals": ["charge_assisted_h_bonding"]},
}


def motif_prior_for_pair(pair: Any) -> dict[str, Any]:
    """Summarize motif priors from a PolymorphPair or pair-like dictionary."""

    molecule = _molecule(pair)
    motifs = _as_list(molecule.get("h_bond_motifs"))
    groups = _as_list(molecule.get("functional_groups"))
    tags = sorted(set(motifs + groups + _as_list(_get(pair, "chemistry_tags"))))
    donors = 0
    acceptors = 0
    signals: list[str] = []
    for tag in tags:
        rule = MOTIF_RULES.get(str(tag).casefold())
        if not rule:
            continue
        donors += int(rule.get("donors", 0))
        acceptors += int(rule.get("acceptors", 0))
        signals.extend(str(signal) for signal in rule.get("signals", []))
    has_charge = bool(molecule.get("has_charge"))
    has_halogen = bool(molecule.get("has_halogen"))
    is_chiral = bool(molecule.get("is_chiral"))
    flexibility = str(molecule.get("flexibility_class") or "unknown")
    complexity = donors + acceptors + (2 if has_charge else 0) + (1 if has_halogen else 0) + (1 if is_chiral else 0)
    if flexibility == "flexible":
        complexity += 2
    elif flexibility == "semi_rigid":
        complexity += 1
    classification = _classify_signal(donors, acceptors, has_charge, complexity)
    return {
        "pair_id": str(_get(pair, "pair_id") or "unknown"),
        "molecule": molecule.get("common_name") or molecule.get("smiles") or "unknown",
        "tags": tags,
        "donor_prior_count": donors,
        "acceptor_prior_count": acceptors,
        "motif_complexity_score": complexity,
        "network_classification": classification,
        "motif_signals": sorted(set(signals)),
        "claim_boundary": "motif priors are explanatory triage signals, not stability evidence",
    }


def motif_prior_report(pairs: Iterable[Any]) -> dict[str, Any]:
    """Build a motif-prior report for pair-like records."""

    rows = [motif_prior_for_pair(pair) for pair in pairs]
    class_counts = Counter(row["network_classification"] for row in rows)
    high_complexity = [row for row in rows if int(row["motif_complexity_score"]) >= 5]
    return {
        "schema_version": "0.1.0",
        "status": "motif_priors_recorded",
        "pair_count": len(rows),
        "network_class_counts": dict(sorted(class_counts.items())),
        "high_complexity_pair_ids": [row["pair_id"] for row in high_complexity],
        "pairs": rows,
        "policy": [
            "Motif priors can prioritize review and explain slices.",
            "Motif priors do not create experimental stability labels.",
            "Verified benchmark claims still require curated evidence and release review.",
        ],
    }


def motif_prior_markdown(report: dict[str, Any]) -> str:
    """Render motif-prior report as Markdown."""

    lines = [
        "# CrystalProbe Motif Priors",
        "",
        f"- Status: `{report['status']}`",
        f"- Pairs: `{report['pair_count']}`",
        "",
        "## Pair Motif Signals",
        "",
        "| Pair | Molecule | Classification | Donors | Acceptors | Complexity | Signals |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in report["pairs"]:
        lines.append(
            f"| `{row['pair_id']}` | {row['molecule']} | `{row['network_classification']}` | "
            f"{row['donor_prior_count']} | {row['acceptor_prior_count']} | "
            f"{row['motif_complexity_score']} | {', '.join(row['motif_signals']) or 'none'} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _classify_signal(donors: int, acceptors: int, has_charge: bool, complexity: int) -> str:
    if has_charge and donors + acceptors > 0:
        return "charge_assisted_h_bond_network"
    if donors > 0 and acceptors > 0 and complexity >= 5:
        return "strong_h_bond_network"
    if donors > 0 and acceptors > 0:
        return "moderate_h_bond_network"
    if acceptors > 0:
        return "acceptor_dominated_contacts"
    return "packing_or_dispersion_dominated"


def _molecule(pair: Any) -> dict[str, Any]:
    molecule = _get(pair, "molecule")
    if hasattr(molecule, "model_dump"):
        return molecule.model_dump(mode="json")
    if isinstance(molecule, dict):
        return molecule
    return {}


def _get(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item is not None]
    return [str(value)]
