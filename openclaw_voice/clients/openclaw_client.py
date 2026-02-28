"""OpenClaw HTTP client with explicit error handling and bounded history."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)


def _trim_history(messages: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    return messages if len(messages) <= limit else messages[-limit:]


def _headers(token: str) -> dict[str, str]:
    base = {"Content-Type": "application/json"}
    return base if not token else {**base, "Authorization": f"Bearer {token}"}


@dataclass
class OpenClawClient:
    """Stateful OpenClaw client for conversational turns."""

    base_url: str
    token: str
    agent_id: str
    history_limit: int
    _history: list[dict[str, str]] | None = None

    @property
    def history(self) -> list[dict[str, str]]:
        """Expose history for tests and diagnostics."""
        if self._history is None:
            self._history = []
        return self._history

    def ask(self, text: str) -> str:
        """Send message to OpenClaw and return reply or explicit error message."""
        self.history.append({"role": "user", "content": text})
        payload: dict[str, Any] = {
            "model": f"openclaw:{self.agent_id}",
            "messages": self.history,
            "stream": False,
            "user": "voice-bridge-local",
        }

        LOGGER.info("openclaw_request_start agent=%s", self.agent_id)
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=_headers(self.token),
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            if not isinstance(reply, str):
                raise ValueError("Unexpected OpenClaw response shape: content is not string")
            self.history.append({"role": "assistant", "content": reply})
            self._history = _trim_history(self.history, self.history_limit)
            LOGGER.info("openclaw_request_done")
            return reply
        except Exception as exc:
            LOGGER.error("openclaw_request_error error=%s", exc)
            return f"OpenClaw request error: {exc}"
