"""Configuration loading for OpenClaw voice bridge."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid float for {name}: {raw}") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid int for {name}: {raw}") from exc


@dataclass(frozen=True)
class VoiceConfig:
    """Static runtime configuration loaded from .env."""

    openclaw_gateway_url: str
    openclaw_gateway_token: str
    openclaw_agent_id: str
    wake_word: str
    wake_sensitivity: float
    silence_seconds: float
    history_limit: int
    voice_session_mode: str = "single"
    session_idle_timeout_sec: float = 15.0
    tts_provider: str = "silero"
    tts_fallback_provider: str = ""
    silero_model_source: str = "snakers4/silero-models"
    silero_language: str = "ru"
    silero_model_id: str = "v4_ru"
    silero_speaker: str = "xenia"
    silero_sample_rate: int = 48000
    silero_cache_dir: str = ".cache/torch"
    speech_max_chunk_chars: int = 220
    log_file: str = "voice_bridge.log"
    lock_file: str = "voice_bridge.lock"

    @staticmethod
    def from_env() -> VoiceConfig:
        """Load and validate runtime config from environment."""
        load_dotenv()
        config = VoiceConfig(
            openclaw_gateway_url=os.getenv(
                "OPENCLAW_GATEWAY_URL", "http://localhost:18789"
            ).strip(),
            openclaw_gateway_token=_require_env("OPENCLAW_GATEWAY_TOKEN"),
            openclaw_agent_id=os.getenv("OPENCLAW_AGENT_ID", "main").strip(),
            wake_word=os.getenv("WAKE_WORD", "jarvis").strip(),
            wake_sensitivity=_env_float("WAKE_SENSITIVITY", 0.6),
            silence_seconds=_env_float("SILENCE_SECONDS", 1.5),
            history_limit=_env_int("HISTORY_LIMIT", 20),
            voice_session_mode=os.getenv("VOICE_SESSION_MODE", "single").strip().lower(),
            session_idle_timeout_sec=_env_float("SESSION_IDLE_TIMEOUT_SEC", 15.0),
            tts_provider=os.getenv("TTS_PROVIDER", "silero").strip().lower(),
            tts_fallback_provider=os.getenv("TTS_FALLBACK_PROVIDER", "").strip().lower(),
            silero_model_source=os.getenv(
                "SILERO_MODEL_SOURCE", "snakers4/silero-models"
            ).strip(),
            silero_language=os.getenv("SILERO_LANGUAGE", "ru").strip(),
            silero_model_id=os.getenv("SILERO_MODEL_ID", "v4_ru").strip(),
            silero_speaker=os.getenv("SILERO_SPEAKER", "xenia").strip(),
            silero_sample_rate=_env_int("SILERO_SAMPLE_RATE", 48000),
            silero_cache_dir=os.getenv("SILERO_CACHE_DIR", ".cache/torch").strip(),
            speech_max_chunk_chars=_env_int("SPEECH_MAX_CHUNK_CHARS", 220),
            lock_file=os.getenv("VOICE_LOCK_FILE", "voice_bridge.lock").strip(),
        )
        _validate_tts_config(config)
        return config


def _validate_tts_config(config: VoiceConfig) -> None:
    supported = {"silero"}
    if config.voice_session_mode not in {"single", "continuous"}:
        raise RuntimeError(
            f"Unsupported VOICE_SESSION_MODE: {config.voice_session_mode}"
        )
    if config.tts_provider not in supported:
        raise RuntimeError(f"Unsupported TTS_PROVIDER: {config.tts_provider}")
    if config.tts_fallback_provider and config.tts_fallback_provider not in supported:
        raise RuntimeError(
            f"Unsupported TTS_FALLBACK_PROVIDER: {config.tts_fallback_provider}"
        )
