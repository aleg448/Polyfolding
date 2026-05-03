"""Dependency-aware adapter discovery."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass


class AdapterNotAvailable(RuntimeError):
    """Raised when an optional scientific backend is not installed."""


@dataclass(frozen=True)
class AdapterAvailability:
    name: str
    available: bool
    required_modules: tuple[str, ...]
    install_hint: str

    @property
    def blocker(self) -> str | None:
        if self.available:
            return None
        modules = ", ".join(self.required_modules)
        return f"{self.name} unavailable: missing Python module(s): {modules}. {self.install_hint}"


ADAPTER_REQUIREMENTS: dict[str, tuple[tuple[str, ...], str]] = {
    "ase_cif": (("ase",), "Install ASE to parse CIF files and construct atomistic structures."),
    "mace_off": (("mace", "torch"), "Install MACE and PyTorch, then configure MACE-OFF checkpoint paths."),
    "aimnet2": (("aimnet",), "Install the AIMNet package with ASE extras and configure model assets."),
    "uma": (("fairchem", "torch"), "Install fairchem/UMA dependencies and model assets."),
    "fastcsp": (("fairchem",), "Clone/install facebookresearch/fairchem with FastCSP extras."),
}


def check_adapter_availability(name: str) -> AdapterAvailability:
    """Check whether a named optional adapter can be imported."""

    if name not in ADAPTER_REQUIREMENTS:
        raise KeyError(f"unknown adapter: {name}")
    modules, hint = ADAPTER_REQUIREMENTS[name]
    available = all(importlib.util.find_spec(module) is not None for module in modules)
    return AdapterAvailability(name=name, available=available, required_modules=modules, install_hint=hint)


def require_adapter(name: str) -> None:
    availability = check_adapter_availability(name)
    if not availability.available:
        raise AdapterNotAvailable(availability.blocker or f"{name} unavailable")


def all_adapter_availability() -> list[AdapterAvailability]:
    return [check_adapter_availability(name) for name in sorted(ADAPTER_REQUIREMENTS)]
