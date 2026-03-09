from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

from openclaw_voice.services.tts_service import TTSService


@dataclass
class StubProvider:
    name: str
    audio_suffix: str
    events: list[str]
    fail: bool = False

    def synthesize(self, text: str, out_path: str) -> None:
        self.events.append(f"synth:{self.name}:{text}")
        Path(out_path).write_bytes(b"audio")
        if self.fail:
            raise RuntimeError("boom")


class StubTTSService(TTSService):
    def __init__(
        self,
        primary: StubProvider,
        fallback: StubProvider | None,
        events: list[str],
    ) -> None:
        super().__init__(
            primary_provider=primary,
            fallback_provider=fallback,
        )
        self.events = events

    def _play_file(self, path: str) -> None:
        self.events.append("play")


def test_tts_runs_hooks_in_order() -> None:
    events: list[str] = []
    primary = StubProvider(name="primary", audio_suffix=".wav", events=events)
    service = StubTTSService(primary=primary, fallback=None, events=events)

    def before() -> None:
        events.append("before")

    def after() -> None:
        events.append("after")

    service.speak("hello", before_speak=before, after_speak=after)
    assert events == ["before", "synth:primary:hello", "play", "after"]


def test_tts_calls_after_hook_on_error() -> None:
    events: list[str] = []
    primary = StubProvider(name="primary", audio_suffix=".wav", events=events, fail=True)
    service = StubTTSService(primary=primary, fallback=None, events=events)
    after = Mock()

    service.speak("hello", after_speak=after)
    after.assert_called_once()


def test_tts_falls_back_to_silero_when_primary_fails() -> None:
    events: list[str] = []
    primary = StubProvider(name="primary", audio_suffix=".wav", events=events, fail=True)
    fallback = StubProvider(name="fallback", audio_suffix=".wav", events=events)
    service = StubTTSService(primary=primary, fallback=fallback, events=events)

    service.speak("hello")

    assert events == ["synth:primary:hello", "synth:fallback:hello", "play"]
