"""URL-scheme guards for reviewer-facing generated HTML.

Generated explorer and viewer pages embed URLs that originate from curation
records and source registries. HTML-escaping those URLs stops attribute
breakout, but it does *not* stop a dangerous scheme such as ``javascript:`` or
``data:`` from executing when the link is clicked or loaded into an ``iframe``.
These helpers keep only plain web links so a source-derived URL cannot become a
script-execution vector in a candidate-safe page.
"""

from __future__ import annotations

_ALLOWED_URL_SCHEMES = ("http://", "https://")


def is_safe_http_url(url: str | None) -> bool:
    """Return True only for absolute ``http://``/``https://`` URLs."""

    if not url:
        return False
    candidate = str(url).strip()
    lowered = candidate.lower()
    return any(lowered.startswith(scheme) for scheme in _ALLOWED_URL_SCHEMES)


def safe_http_url(url: str | None, *, fallback: str = "") -> str:
    """Return the URL when it is a safe web link, otherwise ``fallback``."""

    candidate = str(url).strip() if url else ""
    return candidate if is_safe_http_url(candidate) else fallback
