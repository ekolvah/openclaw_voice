from __future__ import annotations

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
class RecordingClient:
    calls: list[str]

    def ask(self, text: str) -> str:
        self.calls.append(text)
        return f"reply:{text}"


@dataclass
class RecordingTTS:
    calls: list[str]

    def speak(
        self,
        text: str,
        before_speak: object | None = None,
        after_speak: object | None = None,
    ) -> None:
        self.calls.append(text)


class FakeLock:
    def release(self) -> None:
        return None


def test_stop_intent_ends_session_without_tts() -> None:
    recorder = SessionRecorder(text_value="stop", session_calls=[])
    client = RecordingClient(calls=[])
    tts = RecordingTTS(calls=[])
    runner = BridgeRunner(
        recorder=recorder,
        client=client,
        tts=tts,
        instance_lock=FakeLock(),
        session_mode="continuous",
        session_idle_timeout_sec=10.0,
        stop_intent_enabled=True,
        stop_intent_phrases="stop,exit",
    )

    runner.run_once()

    assert recorder.session_calls == [True, False]
    assert client.calls == []
    assert tts.calls == []
    assert runner.state == BridgeState.IDLE


def test_stop_intent_disabled_allows_normal_flow() -> None:
    recorder = SessionRecorder(text_value="stop", session_calls=[])
    client = RecordingClient(calls=[])
    tts = RecordingTTS(calls=[])
    runner = BridgeRunner(
        recorder=recorder,
        client=client,
        tts=tts,
        instance_lock=FakeLock(),
        session_mode="continuous",
        session_idle_timeout_sec=10.0,
        stop_intent_enabled=False,
        stop_intent_phrases="stop,exit",
    )

    runner.run_once()

    assert client.calls == ["stop"]
    assert tts.calls == ["reply:stop"]


def test_stop_intent_matches_short_phrase_with_punctuation() -> None:
    recorder = SessionRecorder(text_value="Stop, please!", session_calls=[])
    client = RecordingClient(calls=[])
    tts = RecordingTTS(calls=[])
    runner = BridgeRunner(
        recorder=recorder,
        client=client,
        tts=tts,
        instance_lock=FakeLock(),
        session_mode="continuous",
        session_idle_timeout_sec=10.0,
        stop_intent_enabled=True,
        stop_intent_phrases="stop,exit",
    )

    runner.run_once()

    assert recorder.session_calls == [True, False]
    assert client.calls == []
    assert tts.calls == []
