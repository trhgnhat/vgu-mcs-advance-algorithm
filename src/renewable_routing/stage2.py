"""Command-line runner for Stage 2 maximum-flow solvers."""

import argparse
import json
import sys
from collections.abc import Sequence

from .edmonds_karp import solve_edmonds_karp
from .ford_fulkerson import solve_ford_fulkerson
from .io import load_network
from .max_flow import MaxFlowProblem, validate_max_flow_result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find and certify a maximum source-to-sink flow."
    )
    parser.add_argument("network", help="path to the network JSON file")
    parser.add_argument("--source", required=True, help="source node ID")
    parser.add_argument("--sink", required=True, help="sink node ID")
    parser.add_argument(
        "--algorithm",
        required=True,
        choices=("ford-fulkerson", "edmonds-karp"),
        help="augmenting-path selection algorithm",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a selected maximum-flow solver and print its certificate."""

    args = _build_parser().parse_args(argv)
    try:
        problem = MaxFlowProblem(
            network=load_network(args.network),
            source=args.source,
            sink=args.sink,
        )
        if args.algorithm == "ford-fulkerson":
            result = solve_ford_fulkerson(problem)
        else:
            result = solve_edmonds_karp(problem)
        validate_max_flow_result(problem, result)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Algorithm: {args.algorithm}")
    print(f"Maximum flow: {result.value}")
    print(f"Cut capacity: {result.cut_capacity}")
    print("Certificate: verified")
    print(f"Augmentations: {result.augmentations}")
    print(f"Flow by edge: {json.dumps(result.flow, sort_keys=True)}")
    print(f"Source side: {json.dumps(sorted(result.source_side))}")
    print(f"Sink side: {json.dumps(sorted(result.sink_side))}")
    print("Cost optimization: not performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
