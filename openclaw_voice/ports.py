"""Typed ports for dependency boundaries."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class RecorderPort(Protocol):
    """Recorder contract used by the app layer."""

    def text(self) -> str:
        """Block until speech is transcribed and return recognized text."""

    def pause(self) -> None:
        """Pause or stop mic capture before TTS playback."""

    def resume(self) -> None:
        """Resume mic capture after TTS playback."""

    def shutdown(self) -> None:
        """Release recorder resources and child processes."""


class OpenClawClientPort(Protocol):
    """OpenClaw chat client contract."""

    def ask(self, text: str) -> str:
        """Send user text and return assistant reply or an error message."""


class TTSServicePort(Protocol):
    """Text-to-speech service contract."""

    def speak(
        self,
        text: str,
        before_speak: Callable[[], None] | None = None,
        after_speak: Callable[[], None] | None = None,
    ) -> None:
        """Speak text and optionally execute lifecycle hooks around playback."""


class InstanceLockPort(Protocol):
    """Cross-process lock contract used by bootstrap and shutdown."""

    def release(self) -> None:
        """Release the process-level singleton lock."""
