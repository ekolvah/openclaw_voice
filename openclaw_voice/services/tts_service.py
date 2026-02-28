"""Edge TTS service with deterministic cleanup and lifecycle hooks."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from collections.abc import Callable

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import edge_tts
import pygame

LOGGER = logging.getLogger(__name__)


class TTSService:
    """Generate and play speech from text."""

    def __init__(self, voice: str) -> None:
        self.voice = voice

    def _synthesize(self, text: str, out_path: str) -> None:
        asyncio.run(edge_tts.Communicate(text, self.voice).save(out_path))

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
        try:
            if before_speak:
                before_speak()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_path = tmp.name
            LOGGER.info("tts_start")
            self._synthesize(text, temp_path)
            self._play_file(temp_path)
            LOGGER.info("tts_done")
        except Exception as exc:
            LOGGER.error("tts_error error=%s", exc)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    LOGGER.error("tts_cleanup_error path=%s", temp_path)
            if after_speak:
                after_speak()
