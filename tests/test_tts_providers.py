from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from openclaw_voice.services.tts_providers import SileroTTSProvider


def test_silero_provider_sets_writable_torch_cache_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    events: dict[str, object] = {}

    class StubModel:
        def to(self, device: str) -> StubModel:
            events["device"] = device
            return self

    def fake_set_dir(path: str) -> None:
        events["cache_dir"] = path

    def fake_load(**kwargs: object) -> tuple[StubModel, object]:
        events["load_kwargs"] = kwargs
        return StubModel(), object()

    torch_stub = SimpleNamespace(
        hub=SimpleNamespace(
            set_dir=fake_set_dir,
            load=fake_load,
        )
    )
    import sys

    monkeypatch.setitem(sys.modules, "torch", torch_stub)

    cache_dir = tmp_path / "torch-cache"
    provider = SileroTTSProvider(
        model_source="snakers4/silero-models",
        language="ru",
        model_id="v4_ru",
        speaker="xenia",
        sample_rate=48000,
        cache_dir=str(cache_dir),
    )

    model = provider._load_model()

    assert isinstance(model, StubModel)
    assert cache_dir.exists()
    assert events["cache_dir"] == str(cache_dir.resolve())
    assert events["device"] == "cpu"
    assert events["load_kwargs"] == {
        "repo_or_dir": "snakers4/silero-models",
        "model": "silero_tts",
        "language": "ru",
        "speaker": "v4_ru",
        "trust_repo": True,
    }
