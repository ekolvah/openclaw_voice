from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from openclaw_voice.app.bridge_runner import BridgeRunner, BridgeState


@dataclass
class SessionRecorder:
    text_value: str
    session_calls: list[bool]

    def text(self) -> str:
        return self.text_value

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def set_session_active(self, active: bool) -> None:
        self.session_calls.append(active)


@dataclass
class FakeClient:
    def ask(self, text: str) -> str:
        return f"reply:{text}"


@dataclass
class FakeTTS:
    def speak(
        self,
        text: str,
        before_speak: Callable[[], None] | None = None,
        after_speak: Callable[[], None] | None = None,
    ) -> None:
        if before_speak:
            before_speak()
        if after_speak:
            after_speak()


class FakeLock:
    def release(self) -> None:
        return None


def test_continuous_mode_starts_session_on_first_speech() -> None:
    recorder = SessionRecorder(text_value="hello", session_calls=[])
    runner = BridgeRunner(
        recorder=recorder,
        client=FakeClient(),
        tts=FakeTTS(),
        instance_lock=FakeLock(),
        session_mode="continuous",
        session_idle_timeout_sec=10.0,
    )

    runner.run_once()

    assert recorder.session_calls == [True]
    assert runner.state == BridgeState.CONVERSING


def test_idle_timeout_ends_session() -> None:
    recorder = SessionRecorder(text_value="", session_calls=[])
    runner = BridgeRunner(
        recorder=recorder,
        client=FakeClient(),
        tts=FakeTTS(),
        instance_lock=FakeLock(),
        session_mode="continuous",
        session_idle_timeout_sec=5.0,
    )
    runner._session_active = True
    runner._session_last_activity = time.monotonic() - 10.0

    runner.run_once()

    assert recorder.session_calls == [False]
    assert runner.state == BridgeState.IDLE
