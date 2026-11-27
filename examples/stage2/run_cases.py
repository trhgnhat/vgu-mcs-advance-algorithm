"""Run the Stage 2 fixtures with both maximum-flow algorithms."""

from pathlib import Path

from renewable_routing.edmonds_karp import solve_edmonds_karp
from renewable_routing.ford_fulkerson import solve_ford_fulkerson
from renewable_routing.io import load_network
from renewable_routing.max_flow import MaxFlowProblem, validate_max_flow_result


EXAMPLES = Path(__file__).parent
CASES = (
    ("rerouting.json", 2, "DFS must cancel its first ab routing choice."),
    ("bottleneck.json", 3, "The a-to-t capacity limits throughput."),
    ("parallel_edges.json", 10, "Both five-unit links count independently."),
    ("opposite_edges.json", 3, "Opposite original edges retain separate IDs."),
    ("disconnected.json", 0, "A disconnected sink has certified value zero."),
    ("lecture_23.json", 23, "Flow equals the known 23-unit cut capacity."),
)
SOLVERS = (
    ("ford-fulkerson", solve_ford_fulkerson),
    ("edmonds-karp", solve_edmonds_karp),
)


def main() -> int:
    """Evaluate every documented fixture and explain its expected maximum."""

    matched = 0
    total = len(CASES) * len(SOLVERS)
    for filename, expected, explanation in CASES:
        problem = MaxFlowProblem(load_network(EXAMPLES / filename), "s", "t")
        print(f"{filename}: {explanation}")
        for display_name, solver in SOLVERS:
            result = solver(problem)
            validate_max_flow_result(problem, result)
            status = "PASS" if result.value == expected else "FAIL"
            if status == "PASS":
                matched += 1
            print(
                f"  {display_name}: {status}; maximum={result.value}; "
                f"cut={result.cut_capacity}; augmentations={result.augmentations}"
            )

    print(f"Summary: {matched}/{total} solver cases matched expected maxima")
    return 0 if matched == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
