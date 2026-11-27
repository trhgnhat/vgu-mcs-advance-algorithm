"""Command-line runner for validating and evaluating a Stage 1 candidate."""

import argparse
import json
import sys
from collections.abc import Sequence

from .evaluation import evaluate_flow
from .io import load_flow, load_network


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a flow network and evaluate a supplied candidate flow."
    )
    parser.add_argument("network", help="path to the network JSON file")
    parser.add_argument("flow", help="path to the candidate-flow JSON file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Stage 1 command-line interface."""

    args = _build_parser().parse_args(argv)
    try:
        network = load_network(args.network)
        flow = load_flow(args.flow)
        evaluation = evaluate_flow(network, flow)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    total_supply = sum(node.balance for node in network.nodes if node.balance > 0)
    total_demand = -sum(node.balance for node in network.nodes if node.balance < 0)

    print("Network structure: valid")
    print("Candidate flow: feasible")
    print(f"Total required supply: {total_supply}")
    print(f"Total required demand: {total_demand}")
    print(f"Total cost: {evaluation.total_cost}")
    print("Optimality: not checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
