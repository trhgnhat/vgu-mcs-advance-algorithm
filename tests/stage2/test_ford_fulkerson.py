"""Ford-Fulkerson behavior and deterministic DFS tests."""

from pathlib import Path

import pytest

from renewable_routing.ford_fulkerson import (
    find_path_dfs,
    solve_ford_fulkerson,
)
from renewable_routing.io import load_network
from renewable_routing.max_flow import (
    MaxFlowProblem,
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
def test_s2t17_ford_fulkerson_solves_every_fixture(
    fixture: str, expected_value: int
) -> None:
    problem = load_problem(fixture)
    result = solve_ford_fulkerson(problem)
    assert result.value == expected_value
    assert result.cut_capacity == expected_value
    assert validate_max_flow_result(problem, result) is None


def test_s2t09_ford_fulkerson_returns_required_rerouting_flow() -> None:
    result = solve_ford_fulkerson(load_problem("rerouting.json"))
    assert result.flow == {"sa": 1, "ab": 0, "bt": 1, "sb": 1, "at": 1}
    assert result.source_side == frozenset({"s"})
    assert result.sink_side == frozenset({"a", "b", "t"})
    assert result.augmentations == 2


def test_s2t12_bottleneck_and_s2t13_parallel_edges() -> None:
    bottleneck_problem = load_problem("bottleneck.json")
    zero_flow = {"sa": 0, "at": 0}
    path = find_path_dfs(build_residual(bottleneck_problem, zero_flow), "s", "t")
    assert path is not None
    updated, delta = augment_flow(bottleneck_problem, zero_flow, path)
    assert delta == 3
    assert updated == {"sa": 3, "at": 3}

    bottleneck = solve_ford_fulkerson(bottleneck_problem)
    assert bottleneck.flow == {"sa": 3, "at": 3}
    assert bottleneck.source_side == frozenset({"s", "a"})
    assert bottleneck.cut_capacity == 3

    parallel = solve_ford_fulkerson(load_problem("parallel_edges.json"))
    assert parallel.flow == {"line_a": 5, "line_b": 5}
    assert parallel.value == parallel.cut_capacity == 10


def test_s2t16_zero_flow_networks_are_successful() -> None:
    disconnected = solve_ford_fulkerson(load_problem("disconnected.json"))
    assert disconnected.value == 0
    assert disconnected.augmentations == 0
    assert disconnected.source_side == frozenset({"s", "a"})

    empty_problem = MaxFlowProblem(
        FlowNetwork((Node("s", 0), Node("t", 0)), ()),
        "s",
        "t",
    )
    empty = solve_ford_fulkerson(empty_problem)
    assert empty.value == empty.cut_capacity == 0
    assert empty.flow == {}
    assert empty.augmentations == 0


def test_s2t21_repeated_solves_have_no_shared_state() -> None:
    problem = load_problem("rerouting.json")
    nodes_before = problem.network.nodes
    edges_before = problem.network.edges
    first = solve_ford_fulkerson(problem)
    first.flow["sa"] = 0
    second = solve_ford_fulkerson(problem)

    assert second.flow == {"sa": 1, "ab": 0, "bt": 1, "sb": 1, "at": 1}
    assert problem.network.nodes == nodes_before
    assert problem.network.edges == edges_before


def test_s2t22_different_edge_order_keeps_the_optimal_value() -> None:
    original = load_problem("rerouting.json")
    reordered = MaxFlowProblem(
        FlowNetwork(
            original.network.nodes,
            tuple(reversed(original.network.edges)),
        ),
        "s",
        "t",
    )
    result = solve_ford_fulkerson(reordered)
    assert result.value == result.cut_capacity == 2
    assert validate_max_flow_result(reordered, result) is None


def test_s2t26_iterative_dfs_handles_a_long_chain() -> None:
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
    result = solve_ford_fulkerson(problem)
    assert result.value == 1
    assert result.augmentations == 1
