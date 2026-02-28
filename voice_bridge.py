"""OpenClaw voice bridge: wake -> STT -> OpenClaw -> TTS."""

from __future__ import annotations

import asyncio
import os
import tempfile
from dataclasses import dataclass
from typing import Any

import edge_tts
import pygame
import requests
from dotenv import load_dotenv
from groq import Groq
from RealtimeSTT import AudioToTextRecorder


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid float for {name}: {raw}") from exc


@dataclass(frozen=True)
class VoiceConfig:
    """Static runtime configuration loaded from .env."""

    picovoice_access_key: str
    groq_api_key: str
    openclaw_gateway_url: str
    openclaw_gateway_token: str
    openclaw_agent_id: str
    tts_voice: str
    wake_sensitivity: float
    silence_seconds: float
    max_record_seconds: float
    history_limit: int = 20

    @staticmethod
    def from_env() -> "VoiceConfig":
        load_dotenv()
        return VoiceConfig(
            picovoice_access_key=_require_env("PICOVOICE_ACCESS_KEY"),
            groq_api_key=_require_env("GROQ_API_KEY"),
            openclaw_gateway_url=os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:18789").strip(),
            openclaw_gateway_token=os.getenv("OPENCLAW_GATEWAY_TOKEN", "").strip(),
            openclaw_agent_id=os.getenv("OPENCLAW_AGENT_ID", "main").strip(),
            tts_voice=os.getenv("EDGE_TTS_VOICE", "ru-RU-DmitryNeural").strip(),
            wake_sensitivity=_env_float("WAKE_SENSITIVITY", 0.6),
            silence_seconds=_env_float("SILENCE_SECONDS", 1.5),
            max_record_seconds=_env_float("MAX_RECORD_SECONDS", 30.0),
        )


def _openclaw_headers(token: str) -> dict[str, str]:
    base = {"Content-Type": "application/json"}
    return base if not token else {**base, "Authorization": f"Bearer {token}"}


def _trim_history(messages: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    return messages if len(messages) <= limit else messages[-limit:]


class VoiceBridge:
    """Bridge orchestration with explicit state and side effects."""

    def __init__(self, config: VoiceConfig) -> None:
        self.config = config
        self.groq_client = Groq(api_key=config.groq_api_key)
        self.history: list[dict[str, str]] = []
        self.recorder: AudioToTextRecorder | None = None

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as file_obj:
            result = self.groq_client.audio.transcriptions.create(
                file=file_obj,
                model="whisper-large-v3",
                language="ru",
            )
        return (getattr(result, "text", "") or "").strip()

    def ask_openclaw(self, text: str) -> str:
        self.history = [*self.history, {"role": "user", "content": text}]
        payload = {
            "model": f"openclaw:{self.config.openclaw_agent_id}",
            "messages": self.history,
            "stream": False,
            "user": "voice-bridge-local",
        }
        response = requests.post(
            f"{self.config.openclaw_gateway_url}/v1/chat/completions",
            headers=_openclaw_headers(self.config.openclaw_gateway_token),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        self.history = _trim_history(
            [*self.history, {"role": "assistant", "content": reply}],
            self.config.history_limit,
        )
        return reply

    def _try_recorder_method(self, methods: tuple[str, ...]) -> None:
        if self.recorder is None:
            return
        for name in methods:
            candidate = getattr(self.recorder, name, None)
            if callable(candidate):
                try:
                    candidate()
                    return
                except Exception:
                    continue

    def speak(self, text: str) -> None:
        self._try_recorder_method(("stop", "pause"))
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_path = tmp.name
            asyncio.run(edge_tts.Communicate(text, self.config.tts_voice).save(temp_path))
            pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        finally:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            self._try_recorder_method(("start", "resume"))

    @staticmethod
    def beep() -> None:
        try:
            import winsound

            winsound.Beep(880, 150)
        except Exception:
            pass

    def handle_text(self, text: str) -> None:
        cleaned = (text or "").strip()
        if not cleaned:
            print("No speech recognized")
            return
        print(f"You: {cleaned}")
        print("Thinking...")
        try:
            reply = self.ask_openclaw(cleaned)
        except Exception as exc:
            reply = f"OpenClaw request error: {exc}"
        print(f"Jarvis: {reply}")
        self.speak(reply)

    def on_recording_stop(self, *args: Any) -> None:
        if not args:
            print("Recording stopped, but callback provided no audio path")
            return
        audio_path = args[0]
        if not isinstance(audio_path, str) or not os.path.exists(audio_path):
            print(f"Unexpected recording callback payload: {type(audio_path)}")
            return
        try:
            self.handle_text(self.transcribe(audio_path))
        except Exception as exc:
            print(f"Transcription error: {exc}")

    def _wake_callback(self) -> None:
        self.beep()
        print("Activated, listening...")

    def build_recorder(self) -> AudioToTextRecorder:
        return AudioToTextRecorder(
            wakeword_backend="pvporcupine",
            wake_words="jarvis",
            wake_words_sensitivity=self.config.wake_sensitivity,
            picovoice_access_key=self.config.picovoice_access_key,
            on_wakeword_detected=self._wake_callback,
            use_microphone=True,
            spinner=False,
            language="ru",
            silero_sensitivity=0.4,
            webrtc_sensitivity=3,
            post_speech_silence_duration=self.config.silence_seconds,
            max_phrase_length=self.config.max_record_seconds,
            model="",
            on_recording_stop=self.on_recording_stop,
        )

    def run_forever(self) -> None:
        print("Loading voice components...")
        self.recorder = self.build_recorder()
        print('Say "Jarvis" to activate')
        try:
            while True:
                self.recorder.listen()
        except KeyboardInterrupt:
            print("Bye")


def main() -> None:
    bridge = VoiceBridge(VoiceConfig.from_env())
    bridge.run_forever()


if __name__ == "__main__":
    main()
