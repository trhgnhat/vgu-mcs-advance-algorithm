"""End-to-end smoke test for the Stage 1 data-case demonstration."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_stage1_example_cases_match_expected_outcomes() -> None:
    result = subprocess.run(
        [sys.executable, "examples/stage1/run_cases.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Summary: 5/5 cases matched expected outcomes" in result.stdout
