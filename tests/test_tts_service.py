from __future__ import annotations

from unittest.mock import Mock

from openclaw_voice.services.tts_service import TTSService


class StubTTSService(TTSService):
    def __init__(self, voice: str, events: list[str], fail_synthesize: bool = False) -> None:
        super().__init__(voice)
        self.events = events
        self.fail_synthesize = fail_synthesize

    def _synthesize(self, text: str, out_path: str) -> None:
        self.events.append("synth")
        if self.fail_synthesize:
            raise RuntimeError("boom")

    def _play_file(self, path: str) -> None:
        self.events.append("play")


def test_tts_runs_hooks_in_order() -> None:
    events: list[str] = []
    service = StubTTSService("ru-RU-DmitryNeural", events)

    def before() -> None:
        events.append("before")

    def after() -> None:
        events.append("after")

    service.speak("hello", before_speak=before, after_speak=after)
    assert events == ["before", "synth", "play", "after"]


def test_tts_calls_after_hook_on_error() -> None:
    events: list[str] = []
    service = StubTTSService("ru-RU-DmitryNeural", events, fail_synthesize=True)
    after = Mock()

    service.speak("hello", after_speak=after)
    after.assert_called_once()
