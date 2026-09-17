from crystalprobe.core.urls import is_safe_http_url, safe_http_url


def test_is_safe_http_url_allows_only_web_schemes():
    assert is_safe_http_url("https://www.crystallography.net/cod/1.html") is True
    assert is_safe_http_url("http://example.org") is True
    assert is_safe_http_url("  https://example.org  ") is True
    assert is_safe_http_url("HTTPS://EXAMPLE.ORG") is True


def test_is_safe_http_url_rejects_dangerous_or_relative_schemes():
    assert is_safe_http_url("javascript:alert(1)") is False
    assert is_safe_http_url("JavaScript:alert(1)") is False
    assert is_safe_http_url("data:text/html,<script>alert(1)</script>") is False
    assert is_safe_http_url("/relative/path") is False
    assert is_safe_http_url("") is False
    assert is_safe_http_url(None) is False


def test_safe_http_url_falls_back_for_unsafe_urls():
    assert safe_http_url("https://example.org") == "https://example.org"
    assert safe_http_url("javascript:alert(1)") == ""
    assert safe_http_url("javascript:alert(1)", fallback="#") == "#"
