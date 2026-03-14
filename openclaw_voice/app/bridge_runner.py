"""Application runner with explicit state machine and lifecycle control."""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import suppress
from enum import StrEnum
from pathlib import Path
from typing import TextIO

from openclaw_voice.adapters.realtimestt_adapter import RealtimeSTTRecorderAdapter
from openclaw_voice.clients.openclaw_client import OpenClawClient
from openclaw_voice.config import VoiceConfig
from openclaw_voice.logging_setup import configure_logging
from openclaw_voice.ports import InstanceLockPort, OpenClawClientPort, RecorderPort, TTSServicePort
from openclaw_voice.services.tts_service import build_tts_service

LOGGER = logging.getLogger(__name__)


class BridgeState(StrEnum):
    """Bridge lifecycle states."""

    IDLE = "IDLE"
    LISTENING = "LISTENING"
    CONVERSING = "CONVERSING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"


class BridgeRunner:
    """Coordinates recorder, OpenClaw client and TTS service."""

    def __init__(
        self,
        recorder: RecorderPort,
        client: OpenClawClientPort,
        tts: TTSServicePort,
        instance_lock: InstanceLockPort,
        session_mode: str = "single",
        session_idle_timeout_sec: float = 15.0,
    ) -> None:
        self.recorder = recorder
        self.client = client
        self.tts = tts
        self.instance_lock = instance_lock
        self.state = BridgeState.IDLE
        self.instance_id = uuid.uuid4().hex[:8]
        self._cycle_no = 0
        self._session_mode = session_mode
        self._session_idle_timeout_sec = session_idle_timeout_sec
        self._session_active = False
        self._session_last_activity: float | None = None

    def _set_state(self, state: BridgeState) -> None:
        if self.state != state:
            LOGGER.info(
                "state_transition instance=%s from=%s to=%s",
                self.instance_id,
                self.state,
                state,
            )
            self.state = state

    @staticmethod
    def _beep() -> None:
        try:
            import winsound

            winsound.Beep(880, 150)
        except Exception:
            LOGGER.error("beep_error")

    def run_once(self) -> None:
        """Process one listen->reply cycle; never raises."""
        self._cycle_no += 1
        cycle_no = self._cycle_no
        started = time.monotonic()
        LOGGER.info("cycle_start instance=%s cycle=%s", self.instance_id, cycle_no)
        self._set_state(
            BridgeState.CONVERSING if self._session_active else BridgeState.LISTENING
        )
        try:
            text = self.recorder.text().strip()
            if not text:
                self._handle_no_speech(cycle_no)
                return

            if self._session_mode == "continuous" and not self._session_active:
                self._start_session(cycle_no)

            LOGGER.info(
                "speech_recognized instance=%s cycle=%s text_len=%s",
                self.instance_id,
                cycle_no,
                len(text),
            )
            self._session_last_activity = time.monotonic()
            self._set_state(BridgeState.PROCESSING)
            reply = self.client.ask(text)

            self._set_state(BridgeState.SPEAKING)
            LOGGER.info(
                "tts_lifecycle instance=%s cycle=%s action=pause_recorder",
                self.instance_id,
                cycle_no,
            )
            self.tts.speak(
                reply,
                before_speak=self.recorder.pause,
                after_speak=self.recorder.resume,
            )
            LOGGER.info(
                "tts_lifecycle instance=%s cycle=%s action=resume_recorder",
                self.instance_id,
                cycle_no,
            )
            if self._session_active:
                self._set_state(BridgeState.CONVERSING)
            else:
                self._set_state(BridgeState.IDLE)
        except Exception as exc:
            LOGGER.error(
                "bridge_cycle_error instance=%s cycle=%s error=%s",
                self.instance_id,
                cycle_no,
                exc,
            )
            self._set_state(BridgeState.IDLE)
        finally:
            elapsed = time.monotonic() - started
            LOGGER.info(
                "cycle_done instance=%s cycle=%s elapsed_sec=%.3f",
                self.instance_id,
                cycle_no,
                elapsed,
            )
        if self._session_active and self._session_last_activity is None:
            self._session_last_activity = started

    def _handle_no_speech(self, cycle_no: int) -> None:
        LOGGER.info(
            "no_speech_recognized instance=%s cycle=%s",
            self.instance_id,
            cycle_no,
        )
        if not self._session_active:
            self._set_state(BridgeState.IDLE)
            return

        now = time.monotonic()
        last = self._session_last_activity or now
        if now - last >= self._session_idle_timeout_sec:
            self._end_session(cycle_no, reason="idle_timeout")
            self._set_state(BridgeState.IDLE)
        else:
            self._set_state(BridgeState.CONVERSING)

    def _start_session(self, cycle_no: int) -> None:
        self._session_active = True
        self._session_last_activity = time.monotonic()
        self._set_state(BridgeState.CONVERSING)
        LOGGER.info(
            "session_start instance=%s cycle=%s mode=%s",
            self.instance_id,
            cycle_no,
            self._session_mode,
        )
        self._set_recorder_session_active(True, cycle_no)

    def _end_session(self, cycle_no: int, reason: str) -> None:
        if not self._session_active:
            return
        self._session_active = False
        self._session_last_activity = None
        LOGGER.info(
            "session_end instance=%s cycle=%s reason=%s",
            self.instance_id,
            cycle_no,
            reason,
        )
        self._set_recorder_session_active(False, cycle_no)

    def _set_recorder_session_active(self, active: bool, cycle_no: int) -> None:
        setter = getattr(self.recorder, "set_session_active", None)
        if callable(setter):
            try:
                setter(active)
                LOGGER.info(
                    "recorder_session_mode instance=%s cycle=%s active=%s",
                    self.instance_id,
                    cycle_no,
                    active,
                )
            except Exception as exc:
                LOGGER.error(
                    "recorder_session_mode_error instance=%s cycle=%s active=%s error=%s",
                    self.instance_id,
                    cycle_no,
                    active,
                    exc,
                )
        else:
            LOGGER.warning(
                "recorder_session_mode_unsupported instance=%s cycle=%s active=%s",
                self.instance_id,
                cycle_no,
                active,
            )

    def shutdown(self) -> None:
        """Release runtime resources in deterministic order."""
        LOGGER.info("bridge_shutdown_start instance=%s", self.instance_id)
        with suppress(Exception):
            self.recorder.shutdown()
        self.instance_lock.release()
        LOGGER.info("bridge_shutdown_done instance=%s", self.instance_id)

    def run_forever(self) -> None:
        """Run bridge loop until interrupted."""
        LOGGER.info("bridge_start instance=%s", self.instance_id)
        try:
            while True:
                self.run_once()
        except KeyboardInterrupt:
            LOGGER.info("bridge_stop instance=%s", self.instance_id)
        finally:
            self.shutdown()


def build_runner() -> BridgeRunner:
    """Construct fully wired runner from environment config."""
    config = VoiceConfig.from_env()
    configure_logging(config.log_file)

    instance_lock = _SingleInstanceLock(config.lock_file)
    if not instance_lock.acquire():
        LOGGER.error(
            "bridge_start_aborted reason=instance_already_running lock_file=%s",
            config.lock_file,
        )
        raise RuntimeError("Another voice bridge instance is already running")

    try:
        adapter = RealtimeSTTRecorderAdapter(
            wake_word=config.wake_word,
            wake_sensitivity=config.wake_sensitivity,
            silence_seconds=config.silence_seconds,
            on_wakeword_detected=BridgeRunner._beep,
            wakeword_backend=config.wakeword_backend,
            picovoice_access_key=config.picovoice_access_key,
            openwakeword_model_paths=config.openwakeword_model_paths,
            openwakeword_inference_framework=config.openwakeword_inference_framework,
        )
        client = OpenClawClient(
            base_url=config.openclaw_gateway_url,
            token=config.openclaw_gateway_token,
            agent_id=config.openclaw_agent_id,
            history_limit=config.history_limit,
        )
        tts = build_tts_service(config)
        return BridgeRunner(
            recorder=adapter.port,
            client=client,
            tts=tts,
            instance_lock=instance_lock,
            session_mode=config.voice_session_mode,
            session_idle_timeout_sec=config.session_idle_timeout_sec,
        )
    except Exception:
        instance_lock.release()
        raise


class _SingleInstanceLock:
    """Cross-process singleton guard for local runtime."""

    def __init__(self, lock_file: str) -> None:
        self.lock_file = lock_file
        self._file: TextIO | None = None
        self._released = False

    def acquire(self) -> bool:
        Path(self.lock_file).parent.mkdir(parents=True, exist_ok=True)
        file_handle = open(self.lock_file, "a+", encoding="utf-8")
        self._file = file_handle
        self._released = False
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
            file_handle.seek(0)
            file_handle.truncate()
            file_handle.write(str(os.getpid()))
            file_handle.flush()
            LOGGER.info("instance_lock_acquired path=%s", self.lock_file)
            return True
        except OSError:
            with suppress(Exception):
                file_handle.close()
            self._file = None
            self._released = True
            return False

    def release(self) -> None:
        if self._released or self._file is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                with suppress(OSError):
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                with suppress(OSError):
                    fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]
        finally:
            with suppress(Exception):
                self._file.close()
            self._file = None
            self._released = True
            LOGGER.info("instance_lock_released path=%s", self.lock_file)
