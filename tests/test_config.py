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


def test_elevenlabs_provider_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")

    cfg = VoiceConfig.from_env()

    assert cfg.tts_provider == "elevenlabs"
    assert cfg.elevenlabs_output_format == "pcm_24000"


def test_elevenlabs_fallback_provider_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "silero")
    monkeypatch.setenv("TTS_FALLBACK_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")

    cfg = VoiceConfig.from_env()

    assert cfg.tts_provider == "silero"
    assert cfg.tts_fallback_provider == "elevenlabs"


def test_elevenlabs_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")

    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
        VoiceConfig.from_env()


def test_elevenlabs_provider_requires_voice_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")

    with pytest.raises(RuntimeError, match="ELEVENLABS_VOICE_ID"):
        VoiceConfig.from_env()


def test_elevenlabs_provider_requires_model_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.delenv("ELEVENLABS_MODEL_ID", raising=False)

    with pytest.raises(RuntimeError, match="ELEVENLABS_MODEL_ID"):
        VoiceConfig.from_env()


def test_partial_elevenlabs_config_requires_full_set(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")

    with pytest.raises(RuntimeError, match="ELEVENLABS_VOICE_ID"):
        VoiceConfig.from_env()


def test_whitespace_elevenlabs_values_are_treated_as_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "   ")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")

    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
        VoiceConfig.from_env()


def test_invalid_elevenlabs_output_format_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")
    monkeypatch.setenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

    with pytest.raises(RuntimeError, match="ELEVENLABS_OUTPUT_FORMAT"):
        VoiceConfig.from_env()


def test_valid_elevenlabs_output_format_loads(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")
    monkeypatch.setenv("ELEVENLABS_OUTPUT_FORMAT", "pcm_44100")

    cfg = VoiceConfig.from_env()

    assert cfg.elevenlabs_output_format == "pcm_44100"


def test_invalid_elevenlabs_connect_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")
    monkeypatch.setenv("ELEVENLABS_CONNECT_TIMEOUT_SEC", "0")

    with pytest.raises(RuntimeError, match="ELEVENLABS_CONNECT_TIMEOUT_SEC"):
        VoiceConfig.from_env()


def test_invalid_elevenlabs_read_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")
    monkeypatch.setenv("ELEVENLABS_READ_TIMEOUT_SEC", "-1")

    with pytest.raises(RuntimeError, match="ELEVENLABS_READ_TIMEOUT_SEC"):
        VoiceConfig.from_env()


def test_elevenlabs_fields_are_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice")
    monkeypatch.setenv("ELEVENLABS_MODEL_ID", "model")
    monkeypatch.setenv("ELEVENLABS_OUTPUT_FORMAT", "pcm_16000")
    monkeypatch.setenv("ELEVENLABS_CONNECT_TIMEOUT_SEC", "6.5")
    monkeypatch.setenv("ELEVENLABS_READ_TIMEOUT_SEC", "45")

    cfg = VoiceConfig.from_env()

    assert cfg.elevenlabs_api_key == "key"  # pragma: allowlist secret
    assert cfg.elevenlabs_voice_id == "voice"
    assert cfg.elevenlabs_model_id == "model"
    assert cfg.elevenlabs_output_format == "pcm_16000"
    assert cfg.elevenlabs_connect_timeout_sec == 6.5
    assert cfg.elevenlabs_read_timeout_sec == 45.0


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
