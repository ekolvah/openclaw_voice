from __future__ import annotations

import tomllib
from pathlib import Path


def test_silero_runtime_dependencies_are_declared_in_pyproject() -> None:
    pyproject = Path("pyproject.toml")
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = set(data["project"]["dependencies"])

    assert "omegaconf" in dependencies
    assert "soundfile" in dependencies


def test_requirements_txt_includes_silero_runtime_dependencies() -> None:
    requirements = {
        line.strip()
        for line in Path("requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert "omegaconf" in requirements
    assert "soundfile" in requirements
