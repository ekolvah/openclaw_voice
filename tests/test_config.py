from __future__ import annotations

import pytest

from openclaw_voice.config import VoiceConfig


def test_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "")
    with pytest.raises(RuntimeError, match="OPENCLAW_GATEWAY_TOKEN"):
        VoiceConfig.from_env()


def test_invalid_float_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.setenv("WAKE_SENSITIVITY", "bad")
    with pytest.raises(RuntimeError, match="WAKE_SENSITIVITY"):
        VoiceConfig.from_env()


def test_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "x")
    monkeypatch.delenv("OPENCLAW_AGENT_ID", raising=False)
    cfg = VoiceConfig.from_env()
    assert cfg.openclaw_agent_id == "main"
    assert cfg.wake_word == "jarvis"
    assert cfg.history_limit > 0
