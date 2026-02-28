"""Logging setup shared by application entrypoints."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_file: str) -> None:
    """Configure console + file logging in one place."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s pid=%(process)d tid=%(thread)d "
            "%(name)s:%(lineno)d %(message)s"
        ),
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
