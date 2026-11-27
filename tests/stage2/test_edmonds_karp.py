"""Edmonds-Karp behavior and deterministic BFS tests."""

from pathlib import Path

import pytest

from renewable_routing.edmonds_karp import find_path_bfs, solve_edmonds_karp
from renewable_routing.io import load_network
from renewable_routing.max_flow import (
    MaxFlowProblem,
    validate_max_flow,
    validate_max_flow_result,
)
from renewable_routing.models import Edge, FlowNetwork, Node
from renewable_routing.residual import augment_flow, build_residual


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage2"


def load_problem(name: str) -> MaxFlowProblem:
    return MaxFlowProblem(load_network(EXAMPLES / name), "s", "t")


@pytest.mark.parametrize(
    ("fixture", "expected_value"),
    (
        ("rerouting.json", 2),
        ("bottleneck.json", 3),
        ("parallel_edges.json", 10),
        ("opposite_edges.json", 3),
        ("disconnected.json", 0),
        ("lecture_23.json", 23),
    ),
)
def test_s2t17_edmonds_karp_solves_every_fixture(
    fixture: str, expected_value: int
) -> None:
    problem = load_problem(fixture)
    result = solve_edmonds_karp(problem)
    assert result.value == expected_value
    assert result.cut_capacity == expected_value
    assert validate_max_flow_result(problem, result) is None


def test_s2t18_lecture_bfs_deltas_and_certificate() -> None:
    problem = load_problem("lecture_23.json")
    flow = {edge.id: 0 for edge in problem.network.edges}
    deltas: list[int] = []

    while True:
        path = find_path_bfs(build_residual(problem, flow), "s", "t")
        if path is None:
            break
        flow, delta = augment_flow(problem, flow, path)
        deltas.append(delta)

    assert deltas == [12, 4, 7]
    assert validate_max_flow(problem, flow) == 23
    result = solve_edmonds_karp(problem)
    assert result.augmentations == 3
    assert result.source_side == frozenset({"s", "v1", "v2", "v4"})
    assert result.sink_side == frozenset({"v3", "t"})


def test_s2t21_candidate_mapping_order_does_not_change_residual_order() -> None:
    problem = load_problem("rerouting.json")
    first = {"sa": 0, "ab": 0, "bt": 0, "sb": 0, "at": 0}
    second = {"at": 0, "sb": 0, "bt": 0, "ab": 0, "sa": 0}
    first_before = first.copy()
    second_before = second.copy()

    first_path = find_path_bfs(build_residual(problem, first), "s", "t")
    second_path = find_path_bfs(build_residual(problem, second), "s", "t")
    assert first_path == second_path
    assert first == first_before
    assert second == second_before


def test_s2t16_edmonds_karp_certifies_a_two_node_empty_graph() -> None:
    problem = MaxFlowProblem(
        FlowNetwork((Node("s", 0), Node("t", 0)), ()),
        "s",
        "t",
    )
    result = solve_edmonds_karp(problem)
    assert result.value == result.cut_capacity == 0
    assert result.flow == {}
    assert result.augmentations == 0
    assert validate_max_flow_result(problem, result) is None


def test_s2t26_iterative_bfs_handles_a_long_chain() -> None:
    length = 1500
    nodes = tuple(Node(f"v{index}", 0) for index in range(length + 1))
    edges = tuple(
        Edge(f"e{index}", f"v{index}", f"v{index + 1}", 1, 0)
        for index in range(length)
    )
    problem = MaxFlowProblem(
        FlowNetwork(nodes, edges),
        "v0",
        f"v{length}",
    )
    result = solve_edmonds_karp(problem)
    assert result.value == 1
    assert result.augmentations == 1
