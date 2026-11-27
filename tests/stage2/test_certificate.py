"""Maximum-flow/minimum-cut certificate and independent-oracle tests."""

import random
from dataclasses import replace
from itertools import combinations
from pathlib import Path

import pytest

from renewable_routing.edmonds_karp import solve_edmonds_karp
from renewable_routing.ford_fulkerson import solve_ford_fulkerson
from renewable_routing.io import load_network
from renewable_routing.max_flow import (
    MaxFlowProblem,
    MaxFlowResult,
    validate_max_flow_result,
)
from renewable_routing.models import Edge, FlowNetwork, Node


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage2"


def rerouting_problem() -> MaxFlowProblem:
    return MaxFlowProblem(load_network(EXAMPLES / "rerouting.json"), "s", "t")


def test_s2t19_rejects_tampered_result_fields() -> None:
    problem = rerouting_problem()
    result = solve_edmonds_karp(problem)
    bad_flow = dict(result.flow)
    bad_flow["sa"] = 0
    tampered = (
        replace(result, value=1),
        replace(result, flow=bad_flow),
        replace(
            result,
            source_side=frozenset({"a"}),
            sink_side=frozenset({"s", "b", "t"}),
        ),
        replace(result, cut_capacity=3),
    )
    for bad_result in tampered:
        with pytest.raises(ValueError):
            validate_max_flow_result(problem, bad_result)


@pytest.mark.parametrize(
    "result",
    (
        MaxFlowResult(
            "unknown",  # type: ignore[arg-type]
            0,
            {},
            frozenset({"s"}),
            frozenset({"t"}),
            0,
            0,
        ),
        MaxFlowResult(
            "edmonds_karp",
            0,
            {},
            frozenset({"s"}),
            frozenset({"t"}),
            0,
            True,
        ),
        MaxFlowResult(
            "edmonds_karp",
            0,
            {},
            frozenset({"s"}),
            frozenset({"t"}),
            0,
            -1,
        ),
        MaxFlowResult(
            "edmonds_karp",
            True,
            {},
            frozenset({"s"}),
            frozenset({"t"}),
            0,
            0,
        ),
        MaxFlowResult(
            "edmonds_karp",
            0,
            {},
            frozenset({"s"}),
            frozenset({"t"}),
            True,
            0,
        ),
    ),
)
def test_s2t20_rejects_invalid_algorithm_and_count_fields(
    result: MaxFlowResult,
) -> None:
    problem = MaxFlowProblem(
        FlowNetwork((Node("s", 0), Node("t", 0)), ()),
        "s",
        "t",
    )
    with pytest.raises(ValueError):
        validate_max_flow_result(problem, result)


def independent_min_cut(problem: MaxFlowProblem) -> int:
    internal = [
        node.id
        for node in problem.network.nodes
        if node.id not in (problem.source, problem.sink)
    ]
    capacities: list[int] = []
    for count in range(len(internal) + 1):
        for selected in combinations(internal, count):
            source_side = {problem.source, *selected}
            capacities.append(
                sum(
                    edge.capacity
                    for edge in problem.network.edges
                    if edge.source in source_side
                    and edge.target not in source_side
                )
            )
    return min(capacities)


def generated_problems() -> list[MaxFlowProblem]:
    generator = random.Random(0)
    problems: list[MaxFlowProblem] = []
    for case_index in range(20):
        node_count = generator.randint(2, 6)
        node_ids = ["s"] + [
            f"v{case_index}_{index}" for index in range(node_count - 2)
        ] + ["t"]
        allowed_pairs = [
            (source, target)
            for source in node_ids
            for target in node_ids
            if source != target and source != "t" and target != "s"
        ]
        edges = tuple(
            Edge(
                f"e{case_index}_{edge_index}",
                *generator.choice(allowed_pairs),
                generator.randint(0, 6),
                0,
            )
            for edge_index in range(generator.randint(0, 12))
        )
        problems.append(
            MaxFlowProblem(
                FlowNetwork(tuple(Node(node_id, 0) for node_id in node_ids), edges),
                "s",
                "t",
            )
        )
    return problems


def test_s2t23_solver_values_equal_independently_enumerated_cuts() -> None:
    for problem in generated_problems():
        expected = independent_min_cut(problem)
        for solver in (solve_ford_fulkerson, solve_edmonds_karp):
            result = solver(problem)
            assert result.value == expected
            assert result.cut_capacity == expected
            assert validate_max_flow_result(problem, result) is None
