from __future__ import annotations

import pytest

from openclaw_voice.config import VoiceConfig


def _disable_dotenv_loading(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("openclaw_voice.config.load_dotenv", lambda: None)


def test_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "")
    with pytest.raises(RuntimeError, match="OPENCLAW_GATEWAY_TOKEN"):
        VoiceConfig.from_env()


def test_invalid_float_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKE_SENSITIVITY", "bad")
    with pytest.raises(RuntimeError, match="WAKE_SENSITIVITY"):
        VoiceConfig.from_env()


def test_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.delenv("OPENCLAW_AGENT_ID", raising=False)
    cfg = VoiceConfig.from_env()
    assert cfg.openclaw_agent_id == "main"
    assert cfg.wake_word == "jarvis"
    assert cfg.history_limit > 0


def test_unsupported_tts_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "future-api")

    with pytest.raises(RuntimeError, match="Unsupported TTS_PROVIDER"):
        VoiceConfig.from_env()


def test_unsupported_voice_session_mode_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("VOICE_SESSION_MODE", "unknown")

    with pytest.raises(RuntimeError, match="VOICE_SESSION_MODE"):
        VoiceConfig.from_env()


def test_unsupported_wakeword_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKEWORD_BACKEND", "other")

    with pytest.raises(RuntimeError, match="WAKEWORD_BACKEND"):
        VoiceConfig.from_env()


def test_unsupported_stt_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("STT_PROVIDER", "other")

    with pytest.raises(RuntimeError, match="STT_PROVIDER"):
        VoiceConfig.from_env()


def test_groq_provider_requires_config(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("STT_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_STT_MODEL", raising=False)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        VoiceConfig.from_env()

    monkeypatch.setenv("GROQ_API_KEY", "key")
    with pytest.raises(RuntimeError, match="GROQ_STT_MODEL"):
        VoiceConfig.from_env()


def test_pvporcupine_requires_wake_word(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKEWORD_BACKEND", "pvporcupine")
    monkeypatch.setenv("WAKE_WORD", "")

    with pytest.raises(RuntimeError, match="WAKE_WORD"):
        VoiceConfig.from_env()


def test_invalid_stop_intent_bool_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("STOP_INTENT_ENABLED", "maybe")

    with pytest.raises(RuntimeError, match="STOP_INTENT_ENABLED"):
        VoiceConfig.from_env()


def test_missing_stop_intent_phrases_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("STOP_INTENT_ENABLED", "true")
    monkeypatch.setenv("STOP_INTENT_PHRASES", "")

    with pytest.raises(RuntimeError, match="STOP_INTENT_PHRASES"):
        VoiceConfig.from_env()


def test_normalizes_wakeword_backend_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKEWORD_BACKEND", "oww")

    cfg = VoiceConfig.from_env()

    assert cfg.wakeword_backend == "openwakeword"


def test_salute_auth_key_not_required_for_silero_only(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "silero")
    monkeypatch.setenv("TTS_FALLBACK_PROVIDER", "")

    cfg = VoiceConfig.from_env()

    assert cfg.tts_provider == "silero"
    assert cfg.tts_fallback_provider == ""


def test_speech_chunk_limit_is_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SPEECH_MAX_CHUNK_CHARS", "123")

    cfg = VoiceConfig.from_env()

    assert cfg.speech_max_chunk_chars == 123


def test_silero_cache_dir_is_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("SILERO_CACHE_DIR", ".cache/custom-torch")

    cfg = VoiceConfig.from_env()

    assert cfg.silero_cache_dir == ".cache/custom-torch"
