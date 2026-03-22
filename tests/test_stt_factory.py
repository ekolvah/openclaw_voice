from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

from openclaw_voice.adapters import stt_factory
from openclaw_voice.config import VoiceConfig
from openclaw_voice.ports import RecorderPort


@dataclass
class DummyRecorder:
    def text(self) -> str:
        return ""

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def shutdown(self) -> None:
        return None


@dataclass
class DummyAdapter:
    port: RecorderPort

    def __init__(self, **_: object) -> None:
        self.port = DummyRecorder()


def _base_config() -> VoiceConfig:
    return VoiceConfig(
        openclaw_gateway_url="http://localhost:18789",
        openclaw_gateway_token="token",
        openclaw_agent_id="main",
        wake_word="jarvis",
        wake_sensitivity=0.6,
        silence_seconds=1.5,
        history_limit=20,
    )


def test_build_recorder_selects_realtimestt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stt_factory, "RealtimeSTTRecorderAdapter", DummyAdapter)
    cfg = replace(_base_config(), stt_provider="realtimestt")

    recorder = stt_factory.build_recorder(cfg, None)

    assert isinstance(recorder, DummyRecorder)


def test_build_recorder_selects_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stt_factory, "GroqSTTRecorderAdapter", DummyAdapter)
    cfg = replace(
        _base_config(),
        stt_provider="groq",
        groq_api_key="test_api_key",  # pragma: allowlist secret
        groq_stt_api_url="http://example",
        groq_stt_model="whisper-large-v3-turbo",
    )

    recorder = stt_factory.build_recorder(cfg, None)

    assert isinstance(recorder, DummyRecorder)
