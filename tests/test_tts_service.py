from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

from openclaw_voice.config import VoiceConfig
from openclaw_voice.services.speech_shaper import RussianSpeechShaper
from openclaw_voice.services.tts_providers import SileroTTSProvider
from openclaw_voice.services.tts_service import TTSService, build_tts_service


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
            shaper=RussianSpeechShaper(max_chunk_chars=32),
        )
        self.events = events

    def _play_file(self, path: str) -> None:
        self.events.append("play")


def test_tts_runs_hooks_in_order() -> None:
    events: list[str] = []
    primary = StubProvider(name="silero", audio_suffix=".wav", events=events)
    service = StubTTSService(primary=primary, fallback=None, events=events)

    def before() -> None:
        events.append("before")

    def after() -> None:
        events.append("after")

    service.speak("hello", before_speak=before, after_speak=after)

    assert events == ["before", "synth:silero:hello", "play", "after"]


def test_tts_calls_after_hook_on_error() -> None:
    events: list[str] = []
    primary = StubProvider(name="silero", audio_suffix=".wav", events=events, fail=True)
    service = StubTTSService(primary=primary, fallback=None, events=events)
    after = Mock()

    service.speak("hello", after_speak=after)

    after.assert_called_once()


def test_tts_falls_back_to_backup_provider_when_primary_fails() -> None:
    events: list[str] = []
    primary = StubProvider(name="silero", audio_suffix=".wav", events=events, fail=True)
    fallback = StubProvider(name="backup", audio_suffix=".wav", events=events)
    service = StubTTSService(primary=primary, fallback=fallback, events=events)

    service.speak("hello")

    assert events == ["synth:silero:hello", "synth:backup:hello", "play"]


def test_shaper_splits_long_markdown_like_reply() -> None:
    shaper = RussianSpeechShaper(max_chunk_chars=35)

    chunks = shaper.shape(
        "# Heading\n"
        "- First item with [link](https://example.com).\n"
        "- Second item is intentionally long."
    )

    assert chunks
    assert all(len(chunk) <= 35 for chunk in chunks)
    assert not any("https://" in chunk for chunk in chunks)
    assert not any("[" in chunk for chunk in chunks)


def test_build_tts_service_uses_silero_primary_and_shaper_limit() -> None:
    config = VoiceConfig(
        openclaw_gateway_url="http://localhost:18789",
        openclaw_gateway_token="token",
        openclaw_agent_id="main",
        wake_word="jarvis",
        wake_sensitivity=0.6,
        silence_seconds=1.5,
        history_limit=20,
        tts_provider="silero",
        tts_fallback_provider="",
        silero_cache_dir=".cache/test-torch",
        speech_max_chunk_chars=77,
    )

    service = build_tts_service(config)

    assert isinstance(service.primary_provider, SileroTTSProvider)
    assert service.primary_provider.name == "silero"
    assert service.fallback_provider is None
    assert isinstance(service.shaper, RussianSpeechShaper)
    assert service.shaper.max_chunk_chars == 77
    assert service.primary_provider.cache_dir == ".cache/test-torch"


def test_build_tts_service_skips_duplicate_fallback_provider() -> None:
    config = VoiceConfig(
        openclaw_gateway_url="http://localhost:18789",
        openclaw_gateway_token="token",
        openclaw_agent_id="main",
        wake_word="jarvis",
        wake_sensitivity=0.6,
        silence_seconds=1.5,
        history_limit=20,
        tts_provider="silero",
        tts_fallback_provider="silero",
        silero_cache_dir=".cache/test-torch",
    )

    service = build_tts_service(config)

    assert isinstance(service.primary_provider, SileroTTSProvider)
    assert service.primary_provider.name == "silero"
    assert service.fallback_provider is None
