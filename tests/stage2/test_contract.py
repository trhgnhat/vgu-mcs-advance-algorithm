"""Stage 2 maximum-flow wrapper and feasible-state contracts."""

from dataclasses import replace

import pytest

from renewable_routing.max_flow import (
    MaxFlowProblem,
    validate_max_flow,
    validate_max_flow_problem,
)
from renewable_routing.models import Edge, FlowNetwork, Node


def make_problem() -> MaxFlowProblem:
    network = FlowNetwork(
        (Node("s", 0), Node("a", 0), Node("t", 0)),
        (
            Edge("sa", "s", "a", 4, 0),
            Edge("at", "a", "t", 3, 0),
        ),
    )
    return MaxFlowProblem(network, "s", "t")


def test_s2t01_supported_problem_and_zero_candidate() -> None:
    problem = make_problem()
    assert validate_max_flow_problem(problem) is None
    assert validate_max_flow(problem, {"sa": 0, "at": 0}) == 0


@pytest.mark.parametrize(
    ("source", "sink", "message"),
    (
        ("missing", "t", "Unknown source"),
        ("s", "missing", "Unknown sink"),
        ("s", "s", "must be distinct"),
        (1, "t", "source must be a string"),
        ("s", None, "sink must be a string"),
    ),
)
def test_s2t02_invalid_terminals(
    source: object, sink: object, message: str
) -> None:
    problem = make_problem()
    invalid = MaxFlowProblem(problem.network, source, sink)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=message):
        validate_max_flow_problem(invalid)


def test_s2t03_rejects_unsupported_fields_without_mutation() -> None:
    problem = make_problem()
    invalid_networks = (
        FlowNetwork(
            (Node("s", 1), Node("a", 0), Node("t", -1)),
            problem.network.edges,
        ),
        replace(
            problem.network,
            edges=(
                Edge("sa", "s", "a", 4, 0, lower_capacity=1),
                problem.network.edges[1],
            ),
        ),
        replace(
            problem.network,
            edges=(
                Edge("sa", "s", "a", 4, 2),
                problem.network.edges[1],
            ),
        ),
    )
    expected = ("balance must be 0", "lower_capacity must be 0", "unit_cost must be 0")

    for network, message in zip(invalid_networks, expected):
        before = network
        with pytest.raises(ValueError, match=message):
            validate_max_flow_problem(MaxFlowProblem(network, "s", "t"))
        assert network == before


@pytest.mark.parametrize(
    ("edge", "message"),
    (
        (Edge("into_s", "a", "s", 0, 0), "enters source"),
        (Edge("out_of_t", "t", "a", 0, 0), "leaves sink"),
        (Edge("loop", "a", "a", 0, 0), "Self-loop"),
    ),
)
def test_s2t04_rejects_terminal_edges_and_self_loops(
    edge: Edge, message: str
) -> None:
    network = FlowNetwork(
        (Node("s", 0), Node("a", 0), Node("t", 0)),
        (edge,),
    )
    with pytest.raises(ValueError, match=message):
        validate_max_flow_problem(MaxFlowProblem(network, "s", "t"))


@pytest.mark.parametrize(
    ("flow", "message"),
    (
        ({"sa": 1.0, "at": 1}, "must be an integer"),
        ({"sa": True, "at": 1}, "must be an integer"),
        ({"sa": "1", "at": 1}, "must be an integer"),
        ({"sa": -1, "at": -1}, "must be nonnegative"),
        ({"sa": 1}, "Missing flow ID"),
        ({"sa": 1, "at": 1, "extra": 0}, "Unknown flow ID"),
    ),
)
def test_s2t05_rejects_invalid_flow_values_and_ids(
    flow: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_max_flow(make_problem(), flow)  # type: ignore[arg-type]


def test_s2t06_rejects_unbalanced_intermediate_node() -> None:
    with pytest.raises(ValueError, match="Node 'a'.*received -1"):
        validate_max_flow(make_problem(), {"sa": 2, "at": 1})


def test_source_value_is_net_outflow_not_sum_of_all_edges() -> None:
    assert validate_max_flow(make_problem(), {"sa": 3, "at": 3}) == 3
