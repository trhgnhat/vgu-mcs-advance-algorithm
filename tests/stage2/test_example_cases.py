"""End-to-end smoke test for the Stage 2 fixture demonstration."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_stage2_example_cases_match_expected_maxima() -> None:
    result = subprocess.run(
        [sys.executable, "examples/stage2/run_cases.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Summary: 12/12 solver cases matched expected maxima" in result.stdout
