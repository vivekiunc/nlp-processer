import app.main as main_module
from fastapi.testclient import TestClient

client = TestClient(main_module.app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_on_success(monkeypatch):
    monkeypatch.setattr(main_module.rag, "answer_query", lambda query, top_k: "fake answer")

    response = client.post("/query", json={"query": "how much water for rice?", "top_k": 2})

    assert response.status_code == 200
    assert response.json() == {"answer": "fake answer"}


def test_query_returns_500_when_pipeline_raises(monkeypatch):
    def boom(query, top_k):
        raise RuntimeError("llm unavailable")

    monkeypatch.setattr(main_module.rag, "answer_query", boom)

    response = client.post("/query", json={"query": "hi"})

    assert response.status_code == 500


def test_query_rejects_empty_query_with_422():
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 422


def test_query_rejects_top_k_out_of_bounds():
    response = client.post("/query", json={"query": "hi", "top_k": 50})
    assert response.status_code == 422


def test_retrieve_returns_chunks_on_success(monkeypatch):
    fake_chunks = [
        {"text": "t", "crop": None, "region": None, "language": None, "source": "s.pdf", "topic": None}
    ]
    monkeypatch.setattr(main_module.rag, "querier", lambda query, top_k: fake_chunks)

    response = client.post("/retrieve", json={"query": "hi"})

    assert response.status_code == 200
    assert response.json()["chunks"][0]["source"] == "s.pdf"


def test_retrieve_returns_500_when_pipeline_raises(monkeypatch):
    def boom(query, top_k):
        raise RuntimeError("chroma unavailable")

    monkeypatch.setattr(main_module.rag, "querier", boom)

    response = client.post("/retrieve", json={"query": "hi"})

    assert response.status_code == 500


def test_audio_query_rejects_unsupported_extension():
    response = client.post(
        "/audio-query", files={"file": ("notes.txt", b"not audio", "text/plain")}
    )
    assert response.status_code == 400


def test_audio_query_succeeds_for_supported_extension(monkeypatch):
    monkeypatch.setattr(main_module.rag, "transcribe", lambda path, language: "transcribed text")
    monkeypatch.setattr(main_module.rag, "answer_query", lambda query, top_k: "final answer")

    response = client.post(
        "/audio-query", files={"file": ("clip.wav", b"RIFF....fake-audio-bytes", "audio/wav")}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcription"] == "transcribed text"
    assert body["answer"] == "final answer"


def test_audio_query_returns_500_when_transcription_fails(monkeypatch):
    def boom(path, language):
        raise RuntimeError("asr model failure")

    monkeypatch.setattr(main_module.rag, "transcribe", boom)

    response = client.post(
        "/audio-query", files={"file": ("clip.wav", b"fake-bytes", "audio/wav")}
    )

    assert response.status_code == 500


def test_audio_query_rejects_unsupported_language():
    response = client.post(
        "/audio-query?language=xx",
        files={"file": ("clip.wav", b"fake-bytes", "audio/wav")},
    )
    assert response.status_code == 400
