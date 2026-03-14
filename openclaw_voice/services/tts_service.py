"""Provider-based TTS orchestration with shaping and fallback."""

from __future__ import annotations

import logging
import os
import tempfile
from collections.abc import Callable

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from openclaw_voice.config import VoiceConfig
from openclaw_voice.ports import SpeechShaperPort, TTSProviderPort
from openclaw_voice.services.speech_shaper import RussianSpeechShaper
from openclaw_voice.services.tts_providers import SileroTTSProvider

LOGGER = logging.getLogger(__name__)


class TTSService:
    """Generate and play speech from text with explicit provider fallback."""

    def __init__(
        self,
        primary_provider: TTSProviderPort,
        fallback_provider: TTSProviderPort | None,
        shaper: SpeechShaperPort,
    ) -> None:
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.shaper = shaper

    def _play_file(self, path: str) -> None:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.quit()

    def speak(
        self,
        text: str,
        before_speak: Callable[[], None] | None = None,
        after_speak: Callable[[], None] | None = None,
    ) -> None:
        """Speak text and run optional hooks around playback."""
        temp_path: str | None = None
        active_provider = self.primary_provider
        chunks = self.shaper.shape(text)
        try:
            if before_speak:
                before_speak()
            if not chunks:
                LOGGER.info("tts_skip reason=empty_shaped_text")
                return

            LOGGER.info(
                "tts_start provider=%s chunks=%s",
                active_provider.name,
                len(chunks),
            )
            for chunk_no, chunk in enumerate(chunks, start=1):
                try:
                    temp_path = self._synthesize_chunk(active_provider, chunk)
                except Exception as exc:
                    LOGGER.error(
                        "tts_provider_error provider=%s chunk=%s error=%s",
                        active_provider.name,
                        chunk_no,
                        exc,
                    )
                    if self.fallback_provider is None or active_provider is self.fallback_provider:
                        raise
                    active_provider = self.fallback_provider
                    LOGGER.info(
                        "tts_provider_fallback from_provider=%s to_provider=%s chunk=%s",
                        self.primary_provider.name,
                        active_provider.name,
                        chunk_no,
                    )
                    temp_path = self._synthesize_chunk(active_provider, chunk)

                self._play_file(temp_path)
                self._cleanup_file(temp_path)
                temp_path = None
            LOGGER.info("tts_done provider=%s", active_provider.name)
        except Exception as exc:
            LOGGER.error("tts_error error=%s", exc)
        finally:
            self._cleanup_file(temp_path)
            if after_speak:
                after_speak()

    def _synthesize_chunk(self, provider: TTSProviderPort, text: str) -> str:
        suffix = provider.audio_suffix or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            out_path = tmp.name
        provider.synthesize(text, out_path)
        return out_path

    @staticmethod
    def _cleanup_file(path: str | None) -> None:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                LOGGER.error("tts_cleanup_error path=%s", path)


def build_tts_service(config: VoiceConfig) -> TTSService:
    """Construct provider-based TTS service from runtime config."""
    primary_provider = _build_provider(config.tts_provider, config)
    fallback_provider = (
        _build_provider(config.tts_fallback_provider, config)
        if config.tts_fallback_provider and config.tts_fallback_provider != config.tts_provider
        else None
    )
    if fallback_provider is not None:
        LOGGER.info(
            "tts_fallback_configured primary=%s fallback=%s",
            primary_provider.name,
            fallback_provider.name,
        )
    shaper = RussianSpeechShaper(max_chunk_chars=config.speech_max_chunk_chars)
    return TTSService(
        primary_provider=primary_provider,
        fallback_provider=fallback_provider,
        shaper=shaper,
    )


def _build_provider(provider_name: str, config: VoiceConfig) -> TTSProviderPort:
    if provider_name == "silero":
        return SileroTTSProvider(
            model_source=config.silero_model_source,
            language=config.silero_language,
            model_id=config.silero_model_id,
            speaker=config.silero_speaker,
            sample_rate=config.silero_sample_rate,
            cache_dir=config.silero_cache_dir,
        )
    raise RuntimeError(f"Unsupported TTS provider: {provider_name}")
