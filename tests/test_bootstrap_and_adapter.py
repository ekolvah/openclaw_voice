from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from openclaw_voice.adapters.realtimestt_adapter import RealtimeSTTRecorderAdapter
from openclaw_voice.app import bridge_runner
from openclaw_voice.config import VoiceConfig
from openclaw_voice.logging_setup import configure_logging


@dataclass
class StubDynamicRecorder:
    calls: list[str]

    def text(self) -> str:
        self.calls.append("text")
        return "hello"

    def stop(self) -> None:
        self.calls.append("stop")

    def start(self) -> None:
        self.calls.append("start")

    def shutdown(self) -> None:
        self.calls.append("shutdown")


def test_adapter_pause_resume_shutdown_calls_dynamic_methods() -> None:
    recorder = StubDynamicRecorder(calls=[])
    adapter = RealtimeSTTRecorderAdapter.__new__(RealtimeSTTRecorderAdapter)
    adapter._recorder = recorder

    assert adapter.text() == "hello"
    adapter.pause()
    adapter.resume()
    adapter.shutdown()

    assert recorder.calls == ["text", "stop", "start", "shutdown"]


def test_single_instance_lock_rejects_second_acquire(tmp_path: Path) -> None:
    lock_path = tmp_path / "voice_bridge.lock"
    first = bridge_runner._SingleInstanceLock(str(lock_path))
    second = bridge_runner._SingleInstanceLock(str(lock_path))

    assert first.acquire() is True
    assert second.acquire() is False

    first.release()


def test_build_runner_aborts_before_adapter_init_when_lock_is_held(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lock_path = tmp_path / "voice_bridge.lock"
    held_lock = bridge_runner._SingleInstanceLock(str(lock_path))
    assert held_lock.acquire() is True

    config = VoiceConfig(
        openclaw_gateway_url="http://localhost:18789",
        openclaw_gateway_token="token",
        openclaw_agent_id="main",
        tts_voice="ru-RU-DmitryNeural",
        wake_word="jarvis",
        wake_sensitivity=0.6,
        silence_seconds=1.5,
        history_limit=20,
        log_file=str(tmp_path / "voice_bridge.log"),
        lock_file=str(lock_path),
    )
    adapter_called = False

    def fake_from_env() -> VoiceConfig:
        return config

    def fake_adapter(*args: object, **kwargs: object) -> object:
        nonlocal adapter_called
        adapter_called = True
        raise AssertionError("adapter must not initialize when lock is already held")

    monkeypatch.setattr(
        "openclaw_voice.app.bridge_runner.VoiceConfig.from_env", staticmethod(fake_from_env)
    )
    monkeypatch.setattr("openclaw_voice.app.bridge_runner.RealtimeSTTRecorderAdapter", fake_adapter)

    with pytest.raises(RuntimeError, match="already running"):
        bridge_runner.build_runner()

    assert adapter_called is False
    held_lock.release()


def test_configure_logging_creates_target_file(tmp_path: Path) -> None:
    log_path = tmp_path / "voice_bridge.log"

    configure_logging(str(log_path))

    assert log_path.exists()
