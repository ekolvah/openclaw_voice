from __future__ import annotations

from unittest.mock import MagicMock, patch

from openclaw_voice.clients.openclaw_client import OpenClawClient


def make_client(limit: int = 20) -> OpenClawClient:
    return OpenClawClient(
        base_url="http://localhost:18789",
        token="token",
        agent_id="main",
        history_limit=limit,
    )


def test_ask_openclaw_returns_reply() -> None:
    client = make_client()
    with patch("openclaw_voice.clients.openclaw_client.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Привет!"}}],
        }
        result = client.ask("Как дела?")
    assert result == "Привет!"


def test_history_trimmed_at_limit() -> None:
    client = make_client(limit=4)
    with patch("openclaw_voice.clients.openclaw_client.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "ok"}}],
        }
        for idx in range(4):
            client.ask(f"q{idx}")
    assert len(client.history) <= 4


def test_openclaw_connection_error_returns_message() -> None:
    client = make_client()
    with patch(
        "openclaw_voice.clients.openclaw_client.requests.post",
        side_effect=Exception("timeout"),
    ):
        result = client.ask("текст")
    assert "OpenClaw request error" in result


def test_openclaw_invalid_json_returns_message() -> None:
    client = make_client()
    with patch("openclaw_voice.clients.openclaw_client.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {"broken": True}
        result = client.ask("текст")
    assert "OpenClaw request error" in result
