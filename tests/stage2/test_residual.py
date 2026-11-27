"""Residual identity, ordering, and safe-update tests."""

from pathlib import Path

import pytest

from renewable_routing.edmonds_karp import find_path_bfs
from renewable_routing.ford_fulkerson import find_path_dfs
from renewable_routing.io import load_network
from renewable_routing.max_flow import MaxFlowProblem, validate_max_flow
from renewable_routing.models import Edge, FlowNetwork, Node
from renewable_routing.residual import (
    ResidualArc,
    augment_flow,
    build_residual,
)


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage2"


def load_problem(name: str) -> MaxFlowProblem:
    return MaxFlowProblem(load_network(EXAMPLES / name), "s", "t")


def test_s2t07_forward_and_reverse_capacities_keep_edge_identity() -> None:
    problem = MaxFlowProblem(
        FlowNetwork(
            (Node("s", 0), Node("t", 0)),
            (Edge("line", "s", "t", 5, 0),),
        ),
        "s",
        "t",
    )
    residual = build_residual(problem, {"line": 3})
    assert residual == {
        "s": (ResidualArc("line", "s", "t", 1, 2),),
        "t": (ResidualArc("line", "t", "s", -1, 3),),
    }


def test_s2t08_zero_capacity_and_isolated_nodes_have_empty_keys() -> None:
    problem = MaxFlowProblem(
        FlowNetwork(
            (Node("s", 0), Node("a", 0), Node("t", 0)),
            (Edge("zero", "s", "a", 0, 0),),
        ),
        "s",
        "t",
    )
    assert build_residual(problem, {"zero": 0}) == {
        "s": (),
        "a": (),
        "t": (),
    }


def test_s2t09_dfs_reroutes_through_reverse_ab() -> None:
    problem = load_problem("rerouting.json")
    flow = {edge.id: 0 for edge in problem.network.edges}

    first_path = find_path_dfs(build_residual(problem, flow), "s", "t")
    assert first_path is not None
    assert [(arc.edge_id, arc.direction) for arc in first_path] == [
        ("sa", 1),
        ("ab", 1),
        ("bt", 1),
    ]
    flow, first_delta = augment_flow(problem, flow, first_path)
    assert first_delta == 1
    assert flow["ab"] == 1

    second_path = find_path_dfs(build_residual(problem, flow), "s", "t")
    assert second_path is not None
    assert [(arc.edge_id, arc.direction) for arc in second_path] == [
        ("sb", 1),
        ("ab", -1),
        ("at", 1),
    ]
    flow, second_delta = augment_flow(problem, flow, second_path)
    assert second_delta == 1
    assert flow == {"sa": 1, "ab": 0, "bt": 1, "sb": 1, "at": 1}
    assert validate_max_flow(problem, flow) == 2


def test_s2t10_bfs_selects_fewest_edge_rerouting_paths() -> None:
    problem = load_problem("rerouting.json")
    flow = {edge.id: 0 for edge in problem.network.edges}
    observed: list[list[tuple[str, int]]] = []

    for _ in range(2):
        path = find_path_bfs(build_residual(problem, flow), "s", "t")
        assert path is not None
        observed.append([(arc.edge_id, arc.direction) for arc in path])
        flow, delta = augment_flow(problem, flow, path)
        assert delta == 1

    assert observed == [
        [("sa", 1), ("at", 1)],
        [("sb", 1), ("bt", 1)],
    ]
    assert validate_max_flow(problem, flow) == 2


def test_s2t11_bad_paths_fail_before_mutating_inputs() -> None:
    problem = load_problem("bottleneck.json")
    flow = {"sa": 0, "at": 0}
    valid = build_residual(problem, flow)
    sa = valid["s"][0]
    at = valid["a"][0]
    bad_paths = (
        (),
        (at,),
        (sa,),
        (ResidualArc("missing", "s", "t", 1, 1),),
        (ResidualArc("sa", "s", "a", 0, 5), at),
        (ResidualArc("sa", "s", "a", 1, 4), at),
        (ResidualArc("sa", "s", "a", 1, 0), at),
        (ResidualArc("sa", "a", "s", 1, 5), at),
    )

    for path in bad_paths:
        before = flow.copy()
        with pytest.raises(ValueError):
            augment_flow(problem, flow, path)
        assert flow == before

    cyclic_problem = MaxFlowProblem(
        FlowNetwork(
            (Node("s", 0), Node("a", 0), Node("b", 0), Node("t", 0)),
            (
                Edge("sa", "s", "a", 2, 0),
                Edge("ab", "a", "b", 1, 0),
                Edge("ba", "b", "a", 1, 0),
                Edge("at", "a", "t", 2, 0),
            ),
        ),
        "s",
        "t",
    )
    cyclic_flow = {"sa": 0, "ab": 0, "ba": 0, "at": 0}
    residual = build_residual(cyclic_problem, cyclic_flow)
    repeated_vertex_path = (
        residual["s"][0],
        next(arc for arc in residual["a"] if arc.edge_id == "ab"),
        next(arc for arc in residual["b"] if arc.edge_id == "ba"),
        next(arc for arc in residual["a"] if arc.edge_id == "at"),
    )
    with pytest.raises(ValueError, match="repeats vertex"):
        augment_flow(cyclic_problem, cyclic_flow, repeated_vertex_path)
    assert cyclic_flow == {"sa": 0, "ab": 0, "ba": 0, "at": 0}


def test_s2t14_opposite_edges_create_four_distinct_residual_arcs() -> None:
    problem = load_problem("opposite_edges.json")
    flow = {"sa": 1, "ab": 2, "ba": 1, "bt": 1}
    residual = build_residual(problem, flow)

    a_to_b = [
        (arc.edge_id, arc.direction, arc.residual_capacity)
        for arc in residual["a"]
        if arc.target == "b"
    ]
    b_to_a = [
        (arc.edge_id, arc.direction, arc.residual_capacity)
        for arc in residual["b"]
        if arc.target == "a"
    ]
    assert a_to_b == [("ab", 1, 1), ("ba", -1, 1)]
    assert b_to_a == [("ab", -1, 2), ("ba", 1, 1)]


def test_s2t15_reverse_ba_cancels_only_that_original_edge() -> None:
    problem = load_problem("opposite_edges.json")
    flow = {"sa": 1, "ab": 2, "ba": 1, "bt": 1}
    before = flow.copy()
    residual = build_residual(problem, flow)
    path = (
        next(arc for arc in residual["s"] if arc.edge_id == "sa"),
        next(
            arc
            for arc in residual["a"]
            if arc.edge_id == "ba" and arc.direction == -1
        ),
        next(arc for arc in residual["b"] if arc.edge_id == "bt"),
    )

    updated, delta = augment_flow(problem, flow, path)
    assert delta == 1
    assert updated == {"sa": 2, "ab": 2, "ba": 0, "bt": 2}
    assert updated["ab"] == flow["ab"] == 2
    assert flow == before
    assert validate_max_flow(problem, updated) == 2
