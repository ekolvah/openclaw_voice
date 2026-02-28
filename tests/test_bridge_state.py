from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from openclaw_voice.app.bridge_runner import BridgeRunner, BridgeState


@dataclass
class FakeRecorder:
    text_value: str
    paused: int = 0
    resumed: int = 0

    def text(self) -> str:
        return self.text_value

    def pause(self) -> None:
        self.paused += 1

    def resume(self) -> None:
        self.resumed += 1


@dataclass
class FakeClient:
    calls: int = 0
    fail: bool = False

    def ask(self, text: str) -> str:
        self.calls += 1
        if self.fail:
            raise RuntimeError("fail")
        return f"reply:{text}"


@dataclass
class FakeTTS:
    calls: int = 0

    def speak(
        self,
        text: str,
        before_speak: Callable[[], None] | None = None,
        after_speak: Callable[[], None] | None = None,
    ) -> None:
        self.calls += 1
        if before_speak:
            before_speak()
        if after_speak:
            after_speak()


def test_empty_text_does_not_call_client_or_tts() -> None:
    recorder = FakeRecorder(text_value="   ")
    client = FakeClient()
    tts = FakeTTS()
    runner = BridgeRunner(recorder=recorder, client=client, tts=tts)

    runner.run_once()

    assert client.calls == 0
    assert tts.calls == 0
    assert runner.state == BridgeState.IDLE


def test_client_error_does_not_crash_cycle() -> None:
    recorder = FakeRecorder(text_value="hello")
    client = FakeClient(fail=True)
    tts = FakeTTS()
    runner = BridgeRunner(recorder=recorder, client=client, tts=tts)

    runner.run_once()

    assert client.calls == 1
    assert tts.calls == 0
    assert runner.state == BridgeState.IDLE


def test_speaking_pauses_and_resumes_recorder() -> None:
    recorder = FakeRecorder(text_value="hello")
    client = FakeClient()
    tts = FakeTTS()
    runner = BridgeRunner(recorder=recorder, client=client, tts=tts)

    runner.run_once()

    assert tts.calls == 1
    assert recorder.paused == 1
    assert recorder.resumed == 1
    assert runner.state == BridgeState.IDLE
