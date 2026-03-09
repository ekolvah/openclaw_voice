from __future__ import annotations

import pytest

from openclaw_voice.config import VoiceConfig


def test_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "")
    with pytest.raises(RuntimeError, match="OPENCLAW_GATEWAY_TOKEN"):
        VoiceConfig.from_env()


def test_invalid_float_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SALUTE_AUTH_KEY", "key")
    monkeypatch.setenv("WAKE_SENSITIVITY", "bad")
    with pytest.raises(RuntimeError, match="WAKE_SENSITIVITY"):
        VoiceConfig.from_env()


def test_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SALUTE_AUTH_KEY", "key")
    monkeypatch.delenv("OPENCLAW_AGENT_ID", raising=False)
    cfg = VoiceConfig.from_env()
    assert cfg.openclaw_agent_id == "main"
    assert cfg.wake_word == "jarvis"
    assert cfg.history_limit > 0


def test_salute_auth_key_required_when_salutespeech_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "salutespeech")
    monkeypatch.setenv("SALUTE_AUTH_KEY", "")

    with pytest.raises(RuntimeError, match="SALUTE_AUTH_KEY"):
        VoiceConfig.from_env()


def test_salute_auth_key_not_required_for_silero_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "silero")
    monkeypatch.setenv("TTS_FALLBACK_PROVIDER", "")
    monkeypatch.setenv("SALUTE_AUTH_KEY", "")

    cfg = VoiceConfig.from_env()

    assert cfg.tts_provider == "silero"
    assert cfg.tts_fallback_provider == ""
