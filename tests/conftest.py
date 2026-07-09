from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def run_cli(tmp_path):
    """Invoke the CLI as a subprocess via ``python -m cfgdiff.cli`` (chosen,
    consistent invocation style for all exit-code/stdout/stderr assertions --
    this exercises the real argparse entry point end to end, not just
    library internals)."""

    def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "cfgdiff.cli", *args],
            capture_output=True,
            text=True,
            cwd=str(cwd or tmp_path),
        )

    return _run


@pytest.fixture
def write(tmp_path):
    """Write *content* to ``tmp_path/name`` and return the Path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    return _write
