"""OpenClaw Voice Bridge entrypoint.

This file intentionally stays thin and delegates runtime logic to package modules.
Environment variables are documented in `openclaw_voice.config`.
"""

from __future__ import annotations

import logging

from openclaw_voice.app.bridge_runner import build_runner


def main() -> None:
    """Bootstrap and run the bridge loop."""
    try:
        build_runner().run_forever()
    except RuntimeError as exc:
        logging.getLogger(__name__).error("voice_bridge_bootstrap_error error=%s", exc)


if __name__ == "__main__":
    main()
