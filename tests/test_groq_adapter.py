from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pytest

from openclaw_voice.adapters.groqstt_adapter import GroqSTTRecorderAdapter


def test_groq_adapter_returns_empty_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = GroqSTTRecorderAdapter.__new__(GroqSTTRecorderAdapter)

    def _boom() -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(adapter, "_record_and_transcribe", _boom)

    assert adapter.text() == ""


@dataclass
class DummyRecorder:
    audio: np.ndarray
    sample_rate: int = 16000

    def wait_audio(self) -> None:
        return None


def test_groq_adapter_records_and_transcribes(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = GroqSTTRecorderAdapter.__new__(GroqSTTRecorderAdapter)
    adapter._recorder = DummyRecorder(audio=np.zeros(320, dtype=np.float32))
    adapter._api_url = "http://example"
    adapter._api_key = "test_api_key"  # pragma: allowlist secret
    adapter._model = "whisper-large-v3-turbo"
    adapter._language = "ru"
    adapter._timeout_sec = 5.0

    class DummyResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json() -> dict[str, str]:
            return {"text": "ok"}

    def fake_post(*args: Any, **kwargs: Any) -> DummyResponse:
        return DummyResponse()

    monkeypatch.setattr("openclaw_voice.adapters.groqstt_adapter.requests.post", fake_post)

    assert adapter.text() == "ok"
