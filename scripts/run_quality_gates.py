"""Run the repository's required local quality gates with a writable cache."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QualityGate:
    """Declarative description of one required repository quality gate."""

    name: str
    command: list[str]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _python_executable(root: Path) -> Path:
    candidates = (
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


def _build_quality_gates(python_executable: Path) -> list[QualityGate]:
    return [
        QualityGate(
            name="detect-secrets",
            command=[
                str(python_executable),
                "-m",
                "pre_commit",
                "run",
                "detect-secrets",
                "--all-files",
            ],
        ),
        QualityGate(
            name="ruff",
            command=[str(python_executable), "-m", "ruff", "check", "."],
        ),
        QualityGate(
            name="mypy",
            command=[str(python_executable), "-m", "mypy", "."],
        ),
        QualityGate(
            name="pytest",
            command=[str(python_executable), "-m", "pytest", "-q"],
        ),
    ]


def _run_gate(gate: QualityGate, root: Path, env: dict[str, str]) -> None:
    LOGGER.info("quality_gate_start gate=%s command=%s", gate.name, gate.command)
    completed = subprocess.run(
        gate.command,
        cwd=root,
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        LOGGER.error("quality_gate_failed gate=%s exit_code=%s", gate.name, completed.returncode)
        raise SystemExit(completed.returncode)
    LOGGER.info("quality_gate_pass gate=%s", gate.name)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    root = _repo_root()
    cache_root = root / ".cache"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_dir = cache_root / f"pre-commit-{uuid.uuid4().hex}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PRE_COMMIT_HOME"] = str(cache_dir)

    python_executable = _python_executable(root)
    LOGGER.info(
        "quality_gate_runner_start root=%s python=%s pre_commit_home=%s",
        root,
        python_executable,
        cache_dir,
    )
    for gate in _build_quality_gates(python_executable):
        _run_gate(gate, root, env)
    LOGGER.info("quality_gate_runner_done gates=%s", 4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
