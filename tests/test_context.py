import sys
from unittest.mock import MagicMock

import context


def test_drop_unverified_citations_keeps_known_sources_and_plain_lines():
    answer = (
        "Apply fertilizer as needed.\n"
        "Source: known.pdf says to use urea.\n"
        "Source: fake.pdf says something else.\n"
        "No source mentioned here."
    )
    retrieved = [{"source": "known.pdf"}, {"source": None}]

    result = context._drop_unverified_citations(answer, retrieved)
    lines = result.splitlines()

    assert "Source: known.pdf says to use urea." in lines
    assert all("fake.pdf" not in line for line in lines)
    assert "No source mentioned here." in lines
    assert "Apply fertilizer as needed." in lines


def test_drop_unverified_citations_handles_no_known_sources():
    answer = "Source: made-up.pdf\nGeneral tip without a source."
    result = context._drop_unverified_citations(answer, retrieved=[])
    assert result == "General tip without a source."


def test_transcribe_returns_text_from_pipeline(monkeypatch):
    monkeypatch.setattr(context, "_get_whisper_asr", lambda language: (lambda audio_path: {"text": "హలో"}))
    assert context.transcribe("some/path.wav") == "హలో"


def test_transcribe_rejects_unsupported_language():
    import pytest

    with pytest.raises(ValueError):
        context.transcribe("some/path.wav", language="xx")


def test_whisper_model_is_lazily_loaded_and_cached_per_language(monkeypatch):
    pipeline_mock = sys.modules["transformers"].pipeline
    monkeypatch.setattr(context, "_whisper_asr", {})
    calls_before = pipeline_mock.call_count

    first = context._get_whisper_asr("te")
    assert pipeline_mock.call_count == calls_before + 1

    second = context._get_whisper_asr("te")
    assert pipeline_mock.call_count == calls_before + 1
    assert first is second

    context._get_whisper_asr("mr")
    assert pipeline_mock.call_count == calls_before + 2
    assert set(context._whisper_asr) == {"te", "mr"}


def test_answer_query_builds_context_block_from_retrieved_chunks(monkeypatch):
    fake_chunks = [
        {"text": "Use urea.", "source": "known.pdf", "topic": "fertilizer", "region": "AP", "crop": None, "language": "en"},
    ]
    monkeypatch.setattr(context, "querier", lambda query, top_k: fake_chunks)

    fake_response = MagicMock()
    fake_response.content = "Source: known.pdf recommends urea.\nSource: made-up.pdf also helps."
    captured = {}

    def fake_invoke(messages):
        captured["messages"] = messages
        return fake_response

    monkeypatch.setattr(context.llm, "invoke", fake_invoke)

    result = context.answer_query("How much fertilizer?", top_k=2)

    assert "known.pdf" in result
    assert "made-up.pdf" not in result
    human_message = captured["messages"][1]
    assert "Use urea." in human_message.content
    assert "How much fertilizer?" in human_message.content


def test_answer_query_falls_back_when_nothing_retrieved(monkeypatch):
    monkeypatch.setattr(context, "querier", lambda query, top_k: [])
    captured = {}

    def fake_invoke(messages):
        captured["messages"] = messages
        response = MagicMock()
        response.content = "General advice, no source."
        return response

    monkeypatch.setattr(context.llm, "invoke", fake_invoke)

    result = context.answer_query("random question")

    assert "No relevant documents found" in captured["messages"][1].content
    assert result == "General advice, no source."


def test_transcribe_and_answer_feeds_transcription_into_answer_query(monkeypatch):
    monkeypatch.setattr(context, "transcribe", lambda path, language: "transcribed query")
    captured = {}

    def fake_answer_query(query, top_k=3):
        captured["query"] = query
        captured["top_k"] = top_k
        return "final answer"

    monkeypatch.setattr(context, "answer_query", fake_answer_query)

    result = context.transcribe_and_answer("audio.wav", top_k=5)

    assert captured == {"query": "transcribed query", "top_k": 5}
    assert result == "final answer"
