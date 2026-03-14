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
        self._wake_word = wake_word
        self._wake_sensitivity = wake_sensitivity
        self._silence_seconds = silence_seconds
        self._on_wakeword_detected = on_wakeword_detected
        self._recorder = self._build_recorder(wake_word_enabled=True)

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

    def shutdown(self) -> None:
        LOGGER.info("recorder_shutdown_start")
        self._call_first_available(("shutdown", "close", "terminate", "stop"))
        LOGGER.info("recorder_shutdown_done")

    def set_session_active(self, active: bool) -> None:
        """Enable or disable wake-word gating for conversation sessions."""
        self._call_first_available(("shutdown", "close", "terminate", "stop"))
        self._recorder = self._build_recorder(wake_word_enabled=not active)

    def _build_recorder(self, wake_word_enabled: bool) -> AudioToTextRecorder:
        wakeword_backend = "pvporcupine" if wake_word_enabled else ""
        wake_words = self._wake_word if wake_word_enabled else ""
        on_wakeword_detected = self._on_wakeword_detected if wake_word_enabled else None
        return AudioToTextRecorder(
            wakeword_backend=wakeword_backend,
            wake_words=wake_words,
            wake_words_sensitivity=self._wake_sensitivity,
            on_wakeword_detected=on_wakeword_detected,
            use_microphone=True,
            spinner=False,
            language="ru",
            silero_sensitivity=0.4,
            webrtc_sensitivity=3,
            post_speech_silence_duration=self._silence_seconds,
            model="tiny",
        )

    def _call_first_available(self, methods: tuple[str, ...]) -> None:
        for name in methods:
            candidate = getattr(self._recorder, name, None)
            if callable(candidate):
                try:
                    candidate()
                    return
                except Exception as exc:
                    LOGGER.error("recorder_method_error method=%s error=%s", name, exc)
        LOGGER.warning("recorder_method_missing methods=%s", ",".join(methods))
