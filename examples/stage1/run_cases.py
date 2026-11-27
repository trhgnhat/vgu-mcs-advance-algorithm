"""Run all Stage 1 data cases as a compact concept demonstration."""

import json
from pathlib import Path
from typing import Any

from renewable_routing.evaluation import evaluate_flow
from renewable_routing.io import load_flow, load_network


EXAMPLE_DIR = Path(__file__).resolve().parent
CASE_FILE = EXAMPLE_DIR / "cases.json"


def _run_case(case: dict[str, Any]) -> bool:
    name = case["name"]
    expected_status = case["expected_status"]
    print(f"\n{name}")

    try:
        network = load_network(EXAMPLE_DIR / case["network"])
        flow = load_flow(EXAMPLE_DIR / case["flow"])
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"  [FAIL] Input error: {error}")
        return False

    try:
        evaluation = evaluate_flow(network, flow)
    except ValueError as error:
        if (
            expected_status == "rejected"
            and case["expected_error"] in str(error)
        ):
            print(f"  [PASS] Rejected as expected: {error}")
            print(f"  Explanation: {case['explanation']}")
            return True

        print(f"  [FAIL] Unexpected rejection: {error}")
        return False

    if expected_status != "feasible":
        print("  [FAIL] Candidate was feasible but rejection was expected")
        return False

    expected_cost = case["expected_cost"]
    if evaluation.total_cost != expected_cost:
        print(
            f"  [FAIL] Expected cost {expected_cost}, "
            f"received {evaluation.total_cost}"
        )
        return False

    balances = ", ".join(
        f"{node_id}={value:+d}"
        for node_id, value in evaluation.net_outflow.items()
    )
    print(f"  [PASS] Feasible; cost={evaluation.total_cost}")
    print(f"  Net outflow: {balances}")
    print(f"  Explanation: {case['explanation']}")
    return True


def main() -> int:
    """Run every Stage 1 case and return nonzero if an outcome differs."""

    try:
        manifest = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        cases = manifest["cases"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError) as error:
        print(f"ERROR: Could not load Stage 1 cases: {error}")
        return 1

    print("Stage 1: supplied-flow validation and evaluation")
    print(manifest["description"])

    passed = sum(_run_case(case) for case in cases)
    total = len(cases)
    print(f"\nSummary: {passed}/{total} cases matched expected outcomes")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
