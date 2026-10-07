import retrieval


class FakeDoc:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata


def make_results(items):
    """items: list of (text, metadata, score) -> what similarity_search_with_score returns."""
    return [(FakeDoc(text, meta), score) for text, meta, score in items]


def test_querier_skips_search_for_duplicate_translation(monkeypatch):
    monkeypatch.setattr(retrieval, "translate", lambda query, lang: query)
    calls = []

    def fake_search(query, k):
        calls.append(query)
        return make_results([("doc1", {"source": "a.pdf"}, 0.1)])

    monkeypatch.setattr(retrieval.vector_store, "similarity_search_with_score", fake_search)

    result = retrieval.querier("hello", top_k=3)

    assert calls == ["hello"]
    assert result[0]["text"] == "doc1"


def test_querier_detects_telugu_and_translates_to_english(monkeypatch):
    seen = {}

    def fake_translate(query, lang):
        seen["lang"] = lang
        return "english version"

    monkeypatch.setattr(retrieval, "translate", fake_translate)
    monkeypatch.setattr(
        retrieval.vector_store,
        "similarity_search_with_score",
        lambda query, k: make_results([("x", {"source": "s"}, 0.1)]),
    )

    retrieval.querier("వరి పంట గురించి", top_k=1)

    assert seen["lang"] == "English"


def test_querier_translates_english_query_to_telugu(monkeypatch):
    seen = {}

    def fake_translate(query, lang):
        seen["lang"] = lang
        return "telugu version"

    monkeypatch.setattr(retrieval, "translate", fake_translate)
    monkeypatch.setattr(
        retrieval.vector_store,
        "similarity_search_with_score",
        lambda query, k: make_results([("x", {"source": "s"}, 0.1)]),
    )

    retrieval.querier("rice crop", top_k=1)

    assert seen["lang"] == "Telugu"


def test_querier_interleaves_variants_and_dedupes_by_source_and_text(monkeypatch):
    monkeypatch.setattr(retrieval, "translate", lambda query, lang: "translated-query")

    def fake_search(query, k):
        if query == "original":
            return make_results([
                ("shared", {"source": "dup.pdf"}, 0.1),
                ("orig-only", {"source": "o.pdf"}, 0.2),
            ])
        return make_results([
            ("shared", {"source": "dup.pdf"}, 0.1),  # same doc the original variant already found
            ("trans-only", {"source": "t.pdf"}, 0.2),
        ])

    monkeypatch.setattr(retrieval.vector_store, "similarity_search_with_score", fake_search)

    result = retrieval.querier("original", top_k=3)

    assert [r["text"] for r in result] == ["shared", "orig-only", "trans-only"]


def test_querier_caps_results_at_top_k(monkeypatch):
    monkeypatch.setattr(retrieval, "translate", lambda query, lang: query)
    monkeypatch.setattr(
        retrieval.vector_store,
        "similarity_search_with_score",
        lambda query, k: make_results([
            ("a", {"source": "a.pdf"}, 0.1),
            ("b", {"source": "b.pdf"}, 0.2),
            ("c", {"source": "c.pdf"}, 0.3),
        ]),
    )

    result = retrieval.querier("q", top_k=2)

    assert len(result) == 2


def test_querier_maps_expected_metadata_fields(monkeypatch):
    monkeypatch.setattr(retrieval, "translate", lambda query, lang: query)
    meta = {"source": "s.pdf", "crop": "rice", "region": "AP", "language": "en", "topic": "irrigation"}
    monkeypatch.setattr(
        retrieval.vector_store,
        "similarity_search_with_score",
        lambda query, k: make_results([("text body", meta, 0.1)]),
    )

    [chunk] = retrieval.querier("q", top_k=1)

    assert chunk == {"text": "text body", **meta}
