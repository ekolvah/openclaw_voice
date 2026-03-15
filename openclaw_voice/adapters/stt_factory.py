"""Recorder factory for STT provider selection."""

from __future__ import annotations

from collections.abc import Callable

from openclaw_voice.adapters.groqstt_adapter import GroqSTTRecorderAdapter
from openclaw_voice.adapters.realtimestt_adapter import RealtimeSTTRecorderAdapter
from openclaw_voice.config import VoiceConfig
from openclaw_voice.ports import RecorderPort


def build_recorder(
    config: VoiceConfig, on_wakeword_detected: Callable[[], None] | None
) -> RecorderPort:
    """Build the recorder adapter for the configured STT provider."""
    if config.stt_provider == "groq":
        groq_adapter = GroqSTTRecorderAdapter(
            wake_word=config.wake_word,
            wake_sensitivity=config.wake_sensitivity,
            silence_seconds=config.silence_seconds,
            on_wakeword_detected=on_wakeword_detected,
            wakeword_backend=config.wakeword_backend,
            picovoice_access_key=config.picovoice_access_key,
            openwakeword_model_paths=config.openwakeword_model_paths,
            openwakeword_inference_framework=config.openwakeword_inference_framework,
            api_url=config.groq_stt_api_url,
            api_key=config.groq_api_key,
            model=config.groq_stt_model,
            language=config.groq_stt_language,
            timeout_sec=config.groq_stt_timeout_sec,
        )
        return groq_adapter.port
    realtime_adapter = RealtimeSTTRecorderAdapter(
        wake_word=config.wake_word,
        wake_sensitivity=config.wake_sensitivity,
        silence_seconds=config.silence_seconds,
        on_wakeword_detected=on_wakeword_detected,
        wakeword_backend=config.wakeword_backend,
        picovoice_access_key=config.picovoice_access_key,
        openwakeword_model_paths=config.openwakeword_model_paths,
        openwakeword_inference_framework=config.openwakeword_inference_framework,
    )
    return realtime_adapter.port
