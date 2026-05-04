"""Crystallography Open Database query helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


COD_BASE_URL = "https://www.crystallography.net/cod"


@dataclass(frozen=True)
class CodQuery:
    """A COD search query with provenance-friendly labeling."""

    query_id: str
    params: dict[str, str]
    description: str

    def url(self) -> str:
        params = dict(self.params)
        params["format"] = "json"
        return f"{COD_BASE_URL}/result.php?{urlencode(params)}"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self) | {"url": self.url()}


def query_cod(query: CodQuery, *, timeout: int = 30) -> list[dict[str, Any]]:
    """Run one COD JSON query."""

    with urlopen(query.url(), timeout=timeout) as response:  # noqa: S310 - fixed public COD endpoint.
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError(f"COD returned non-list payload for {query.query_id}")
    return data


def lisdexamfetamine_cod_queries() -> list[CodQuery]:
    """COD queries for lisdexamfetamine dimesylate source discovery."""

    return [
        CodQuery(
            query_id="text_lisdexamfetamine",
            params={"text1": "lisdexamfetamine"},
            description="Exact modern INN spelling in COD text fields.",
        ),
        CodQuery(
            query_id="text_lisdexamphetamine",
            params={"text1": "lisdexamphetamine"},
            description="Patent spelling variant used in US7659253.",
        ),
        CodQuery(
            query_id="text_amphetamine_dimesylate",
            params={"text1": "amphetamine", "text2": "dimesylate"},
            description="Broad text query for amphetamine dimesylate wording.",
        ),
        CodQuery(
            query_id="formula_salt_exact",
            params={"formula": "C17 H33 N3 O7 S2"},
            description="Exact PubChem salt formula.",
        ),
        CodQuery(
            query_id="cell_window_chons",
            params={
                "el1": "C",
                "el2": "H",
                "el3": "N",
                "el4": "O",
                "el5": "S",
                "vmin": "2200",
                "vmax": "2300",
            },
            description="Loose CHNOS cell-volume window around the patent lattice volume.",
        ),
    ]
