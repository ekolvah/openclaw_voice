"""TTS provider implementations for the voice bridge."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, cast

import requests

LOGGER = logging.getLogger(__name__)


@dataclass
class SaluteSpeechTTSProvider:
    """SaluteSpeech REST TTS provider."""

    auth_key: str
    auth_url: str
    api_url: str
    scope: str
    voice: str
    sample_rate: int
    request_timeout_sec: int
    name: str = "salutespeech"
    audio_suffix: str = ".wav"
    _access_token: str | None = None
    _expires_at_epoch: float = 0.0

    def synthesize(self, text: str, out_path: str) -> None:
        token = self._get_access_token()
        params: dict[str, str | int] = {
            "voice": self.voice,
            "format": "wav16",
            "sample_rate": self.sample_rate,
        }
        response = requests.post(
            self.api_url,
            params=params,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "text/plain; charset=utf-8",
                "X-Request-ID": str(uuid.uuid4()),
            },
            data=text.encode("utf-8"),
            timeout=self.request_timeout_sec,
        )
        response.raise_for_status()
        with open(out_path, "wb") as file_handle:
            file_handle.write(response.content)

    def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._expires_at_epoch - 60:
            return self._access_token

        response = requests.post(
            self.auth_url,
            headers={
                "Authorization": f"Basic {self.auth_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "RqUID": str(uuid.uuid4()),
            },
            data={"scope": self.scope},
            timeout=self.request_timeout_sec,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("SaluteSpeech auth response missing access_token")

        expires_at = data.get("expires_at")
        if isinstance(expires_at, (int, float)):
            self._expires_at_epoch = (
                float(expires_at) / 1000
                if expires_at > 10_000_000_000
                else float(expires_at)
            )
        else:
            self._expires_at_epoch = time.time() + 1800
        self._access_token = token
        return token


@dataclass
class SileroTTSProvider:
    """Silero TTS provider loaded lazily through torch hub."""

    model_source: str
    language: str
    model_id: str
    speaker: str
    sample_rate: int
    device: str = "cpu"
    name: str = "silero"
    audio_suffix: str = ".wav"
    _model: Any | None = None

    def synthesize(self, text: str, out_path: str) -> None:
        import soundfile  # type: ignore[import-untyped]

        model = self._load_model()
        audio = model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            put_accent=True,
            put_yo=True,
        )
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        soundfile.write(out_path, audio, self.sample_rate)

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        import torch

        LOGGER.info(
            "silero_model_load_start source=%s language=%s model_id=%s",
            self.model_source,
            self.language,
            self.model_id,
        )
        load = cast(Any, torch.hub.load)
        model, _ = load(
            repo_or_dir=self.model_source,
            model="silero_tts",
            language=self.language,
            speaker=self.model_id,
            trust_repo=True,
        )
        if hasattr(model, "to"):
            model.to(self.device)
        self._model = model
        LOGGER.info("silero_model_load_done source=%s", self.model_source)
        return model
