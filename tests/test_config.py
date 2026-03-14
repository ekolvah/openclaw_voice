from __future__ import annotations

import pytest

from openclaw_voice.config import VoiceConfig


def test_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "")
    with pytest.raises(RuntimeError, match="OPENCLAW_GATEWAY_TOKEN"):
        VoiceConfig.from_env()


def test_invalid_float_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKE_SENSITIVITY", "bad")
    with pytest.raises(RuntimeError, match="WAKE_SENSITIVITY"):
        VoiceConfig.from_env()


def test_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.delenv("OPENCLAW_AGENT_ID", raising=False)
    cfg = VoiceConfig.from_env()
    assert cfg.openclaw_agent_id == "main"
    assert cfg.wake_word == "jarvis"
    assert cfg.history_limit > 0


def test_unsupported_tts_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "future-api")

    with pytest.raises(RuntimeError, match="Unsupported TTS_PROVIDER"):
        VoiceConfig.from_env()


def test_unsupported_voice_session_mode_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("VOICE_SESSION_MODE", "unknown")

    with pytest.raises(RuntimeError, match="VOICE_SESSION_MODE"):
        VoiceConfig.from_env()


def test_salute_auth_key_not_required_for_silero_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "silero")
    monkeypatch.setenv("TTS_FALLBACK_PROVIDER", "")

    cfg = VoiceConfig.from_env()

    assert cfg.tts_provider == "silero"
    assert cfg.tts_fallback_provider == ""


def test_speech_chunk_limit_is_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SPEECH_MAX_CHUNK_CHARS", "123")

    cfg = VoiceConfig.from_env()

    assert cfg.speech_max_chunk_chars == 123


def test_silero_cache_dir_is_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SILERO_CACHE_DIR", ".cache/custom-torch")

    cfg = VoiceConfig.from_env()

    assert cfg.silero_cache_dir == ".cache/custom-torch"
