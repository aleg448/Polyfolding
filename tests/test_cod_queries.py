from crystalprobe.datahub.cod import lisdexamfetamine_cod_queries


def test_lisdexamfetamine_cod_queries_have_json_urls():
    queries = lisdexamfetamine_cod_queries()
    assert {query.query_id for query in queries} >= {"text_lisdexamfetamine", "formula_salt_exact"}
    for query in queries:
        url = query.url()
        assert url.startswith("https://www.crystallography.net/cod/result.php?")
        assert "format=json" in url
