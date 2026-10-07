from unittest.mock import MagicMock

import llm_client


def test_translate_returns_stripped_content(monkeypatch):
    fake_response = MagicMock()
    fake_response.content = "  హలో  "
    monkeypatch.setattr(llm_client.llm, "invoke", lambda messages: fake_response)

    result = llm_client.translate("hello", "Telugu")

    assert result == "హలో"


def test_translate_sends_target_language_and_text(monkeypatch):
    captured = {}

    def fake_invoke(messages):
        captured["messages"] = messages
        response = MagicMock()
        response.content = "ok"
        return response

    monkeypatch.setattr(llm_client.llm, "invoke", fake_invoke)

    llm_client.translate("water the crop", "Telugu")

    system_message, human_message = captured["messages"]
    assert "Telugu" in system_message.content
    assert human_message.content == "water the crop"
