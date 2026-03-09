"""Configuration loading for OpenClaw voice bridge.

Environment variables:
- OPENCLAW_GATEWAY_URL
- OPENCLAW_GATEWAY_TOKEN
- OPENCLAW_AGENT_ID
- TTS_PROVIDER
- TTS_FALLBACK_PROVIDER
- SALUTE_AUTH_URL
- SALUTE_API_URL
- SALUTE_AUTH_KEY
- SALUTE_SCOPE
- SALUTE_VOICE
- SALUTE_SAMPLE_RATE
- SILERO_MODEL_SOURCE
- SILERO_LANGUAGE
- SILERO_MODEL_ID
- SILERO_SPEAKER
- SILERO_SAMPLE_RATE
- SPEECH_MAX_CHUNK_CHARS
- WAKE_WORD
- WAKE_SENSITIVITY
- SILENCE_SECONDS
- HISTORY_LIMIT
- VOICE_LOCK_FILE
"""

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
    tts_provider: str = "silero"
    tts_fallback_provider: str = ""
    salute_auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    salute_api_url: str = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
    salute_auth_key: str = ""
    salute_scope: str = "SALUTE_SPEECH_PERS"
    salute_voice: str = "Nec_24000"
    salute_sample_rate: int = 24000
    silero_model_source: str = "snakers4/silero-models"
    silero_language: str = "ru"
    silero_model_id: str = "v4_ru"
    silero_speaker: str = "xenia"
    silero_sample_rate: int = 48000
    speech_max_chunk_chars: int = 220
    tts_request_timeout_sec: int = 60
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
            tts_provider=os.getenv("TTS_PROVIDER", "silero").strip().lower(),
            tts_fallback_provider=os.getenv("TTS_FALLBACK_PROVIDER", "").strip().lower(),
            salute_auth_url=os.getenv(
                "SALUTE_AUTH_URL",
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            ).strip(),
            salute_api_url=os.getenv(
                "SALUTE_API_URL",
                "https://smartspeech.sber.ru/rest/v1/text:synthesize",
            ).strip(),
            salute_auth_key=os.getenv("SALUTE_AUTH_KEY", "").strip(),
            salute_scope=os.getenv("SALUTE_SCOPE", "SALUTE_SPEECH_PERS").strip(),
            salute_voice=os.getenv("SALUTE_VOICE", "Nec_24000").strip(),
            salute_sample_rate=_env_int("SALUTE_SAMPLE_RATE", 24000),
            silero_model_source=os.getenv(
                "SILERO_MODEL_SOURCE", "snakers4/silero-models"
            ).strip(),
            silero_language=os.getenv("SILERO_LANGUAGE", "ru").strip(),
            silero_model_id=os.getenv("SILERO_MODEL_ID", "v4_ru").strip(),
            silero_speaker=os.getenv("SILERO_SPEAKER", "xenia").strip(),
            silero_sample_rate=_env_int("SILERO_SAMPLE_RATE", 48000),
            speech_max_chunk_chars=_env_int("SPEECH_MAX_CHUNK_CHARS", 220),
            tts_request_timeout_sec=_env_int("TTS_REQUEST_TIMEOUT_SEC", 60),
            lock_file=os.getenv("VOICE_LOCK_FILE", "voice_bridge.lock").strip(),
        )
        _validate_tts_config(config)
        return config


def _validate_tts_config(config: VoiceConfig) -> None:
    supported = {"salutespeech", "silero"}
    if config.tts_provider not in supported:
        raise RuntimeError(f"Unsupported TTS_PROVIDER: {config.tts_provider}")
    if config.tts_fallback_provider and config.tts_fallback_provider not in supported:
        raise RuntimeError(
            f"Unsupported TTS_FALLBACK_PROVIDER: {config.tts_fallback_provider}"
        )
    if config.tts_provider == "salutespeech" and not config.salute_auth_key:
        raise RuntimeError("Missing required environment variable: SALUTE_AUTH_KEY")
    if config.tts_fallback_provider == "salutespeech" and not config.salute_auth_key:
        raise RuntimeError("Missing required environment variable: SALUTE_AUTH_KEY")
