"""TTS provider implementations for the voice bridge."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, cast

LOGGER = logging.getLogger(__name__)


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
