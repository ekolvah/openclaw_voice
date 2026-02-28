"""Typed adapter around RealtimeSTT's dynamic API."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import cast

from RealtimeSTT import AudioToTextRecorder

from openclaw_voice.ports import RecorderPort

LOGGER = logging.getLogger(__name__)


class RealtimeSTTRecorderAdapter:
    """Adapter that isolates untyped/dynamic RealtimeSTT calls."""

    def __init__(
        self,
        wake_word: str,
        wake_sensitivity: float,
        silence_seconds: float,
        on_wakeword_detected: Callable[[], None] | None,
    ) -> None:
        self._recorder = AudioToTextRecorder(
            wakeword_backend="pvporcupine",
            wake_words=wake_word,
            wake_words_sensitivity=wake_sensitivity,
            on_wakeword_detected=on_wakeword_detected,
            use_microphone=True,
            spinner=False,
            language="ru",
            silero_sensitivity=0.4,
            webrtc_sensitivity=3,
            post_speech_silence_duration=silence_seconds,
            model="tiny",
        )

    @property
    def port(self) -> RecorderPort:
        """Expose a typed recorder port."""
        return cast(RecorderPort, self)

    def text(self) -> str:
        return str(self._recorder.text() or "")

    def pause(self) -> None:
        self._call_first_available(("stop", "pause"))

    def resume(self) -> None:
        self._call_first_available(("start", "resume"))

    def _call_first_available(self, methods: tuple[str, ...]) -> None:
        for name in methods:
            candidate = getattr(self._recorder, name, None)
            if callable(candidate):
                try:
                    candidate()
                    return
                except Exception as exc:
                    LOGGER.error("recorder_method_error method=%s error=%s", name, exc)
