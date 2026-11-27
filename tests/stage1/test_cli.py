"""Required Stage 1 CLI outcomes."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage1"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "renewable_routing.stage1", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_t22_cli_fixture_outcomes() -> None:
    feasible_cases = (
        ("two_link_network.json", "flow_optimal.json", 6, 9),
        ("two_link_network.json", "flow_feasible_nonoptimal.json", 6, 15),
        ("transit_network.json", "transit_flow.json", 4, 20),
    )
    for network_name, flow_name, required_amount, expected_cost in feasible_cases:
        result = run_cli(
            str(EXAMPLES / network_name),
            str(EXAMPLES / flow_name),
        )
        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout.splitlines() == [
            "Network structure: valid",
            "Candidate flow: feasible",
            f"Total required supply: {required_amount}",
            f"Total required demand: {required_amount}",
            f"Total cost: {expected_cost}",
            "Optimality: not checked",
        ]

    rejected_cases = (
        ("flow_over_capacity.json", "flow 6 exceeds capacity 5"),
        ("flow_under_delivery.json", "expected net outflow 6, received 5"),
    )
    for flow_name, expected_error in rejected_cases:
        result = run_cli(
            str(EXAMPLES / "two_link_network.json"),
            str(EXAMPLES / flow_name),
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert result.stderr.startswith("ERROR:")
        assert expected_error in result.stderr
        assert "optimal" not in result.stderr.lower()
        assert "infeasible" not in result.stderr.lower()
        assert "cost" not in result.stderr.lower()


def test_t20_cli_input_and_usage_errors() -> None:
    missing_file = run_cli(
        str(EXAMPLES / "missing.json"),
        str(EXAMPLES / "flow_optimal.json"),
    )
    assert missing_file.returncode == 1
    assert missing_file.stdout == ""
    assert missing_file.stderr.startswith("ERROR:")

    usage_error = run_cli()
    assert usage_error.returncode == 2
    assert "usage:" in usage_error.stderr.lower()
