"""Stage 2 CLI output and exit-code contracts."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage2"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "renewable_routing.stage2", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_s2t24_cli_success_output() -> None:
    result = run_cli(
        str(EXAMPLES / "rerouting.json"),
        "--source",
        "s",
        "--sink",
        "t",
        "--algorithm",
        "ford-fulkerson",
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        "Algorithm: ford-fulkerson",
        "Maximum flow: 2",
        "Cut capacity: 2",
        "Certificate: verified",
        "Augmentations: 2",
        'Flow by edge: {"ab": 0, "at": 1, "bt": 1, "sa": 1, "sb": 1}',
        'Source side: ["s"]',
        'Sink side: ["a", "b", "t"]',
        "Cost optimization: not performed",
    ]


def test_s2t24_cli_zero_flow_is_verified_success() -> None:
    result = run_cli(
        str(EXAMPLES / "disconnected.json"),
        "--source",
        "s",
        "--sink",
        "t",
        "--algorithm",
        "edmonds-karp",
    )
    assert result.returncode == 0
    assert "Maximum flow: 0" in result.stdout
    assert "Cut capacity: 0" in result.stdout
    assert "Certificate: verified" in result.stdout
    assert "Cost optimization: not performed" in result.stdout


def test_s2t24_cli_usage_errors_exit_two() -> None:
    missing_arguments = run_cli()
    assert missing_arguments.returncode == 2
    assert "usage:" in missing_arguments.stderr.lower()

    invalid_algorithm = run_cli(
        str(EXAMPLES / "rerouting.json"),
        "--source",
        "s",
        "--sink",
        "t",
        "--algorithm",
        "not-a-solver",
    )
    assert invalid_algorithm.returncode == 2
    assert "invalid choice" in invalid_algorithm.stderr


def test_s2t24_cli_input_failures_exit_one(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"nodes": [}', encoding="utf-8")
    cases = (
        (str(EXAMPLES / "missing.json"), "s", "t"),
        (str(malformed), "s", "t"),
        (
            str(ROOT / "examples" / "stage1" / "two_link_network.json"),
            "source",
            "city",
        ),
    )
    for path, source, sink in cases:
        result = run_cli(
            path,
            "--source",
            source,
            "--sink",
            sink,
            "--algorithm",
            "edmonds-karp",
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert result.stderr.startswith("ERROR:")
        assert "Certificate: verified" not in result.stderr
