"""Required Stage 1 behavior, grouped by data scenario."""

import json
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

from renewable_routing.evaluation import evaluate_flow
from renewable_routing.io import load_flow, load_network
from renewable_routing.models import Edge, FlowEvaluation, FlowNetwork, Node
from renewable_routing.validation import validate_flow, validate_network


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples" / "stage1"


def primary_network() -> FlowNetwork:
    return FlowNetwork(
        (Node("source", 6), Node("city", -6)),
        (
            Edge("line_a", "source", "city", 5, 1),
            Edge("line_b", "source", "city", 5, 4),
        ),
    )


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_required_models_and_defaults() -> None:
    assert [field.name for field in fields(Node)] == ["id", "balance"]
    assert [field.name for field in fields(Edge)] == [
        "id",
        "source",
        "target",
        "capacity",
        "unit_cost",
        "lower_capacity",
    ]
    assert [field.name for field in fields(FlowNetwork)] == ["nodes", "edges"]
    assert [field.name for field in fields(FlowEvaluation)] == [
        "total_cost",
        "net_outflow",
    ]
    assert Edge("line", "source", "city", 5, 2).lower_capacity == 0

    for instance, attribute, value in (
        (Node("u", 0), "balance", 1),
        (Edge("e", "u", "v", 1, 1), "capacity", 2),
        (FlowNetwork((Node("u", 0),), ()), "nodes", ()),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, attribute, value)


def test_t01_to_t04_two_link_fixture_outcomes() -> None:
    network = load_network(EXAMPLES / "two_link_network.json")
    feasible_cases = (
        ("flow_optimal.json", 9),
        ("flow_feasible_nonoptimal.json", 15),
    )
    for filename, expected_cost in feasible_cases:
        result = evaluate_flow(network, load_flow(EXAMPLES / filename))
        assert result.total_cost == expected_cost
        assert result.net_outflow == {"source": 6, "city": -6}
        assert not hasattr(result, "is_optimal")

    rejected_cases = (
        ("flow_over_capacity.json", "flow 6 exceeds capacity 5"),
        ("flow_under_delivery.json", "expected net outflow 6, received 5"),
    )
    for filename, expected_error in rejected_cases:
        with pytest.raises(ValueError, match=expected_error):
            evaluate_flow(network, load_flow(EXAMPLES / filename))


def test_t05_t06_candidate_values_and_edge_ids() -> None:
    network = primary_network()
    invalid_cases = (
        ({"line_a": -1, "line_b": 7}, "below lower_capacity"),
        ({"line_a": 5}, "Missing flow ID"),
        ({"line_a": 5, "line_b": 1, "unknown": 0}, "Unknown flow ID"),
    )
    for flow, expected_error in invalid_cases:
        with pytest.raises(ValueError, match=expected_error):
            validate_flow(network, flow)


def test_t07_to_t10_network_structure_errors() -> None:
    invalid_networks = (
        (
            FlowNetwork((Node("same", 0), Node("same", 0)), ()),
            "Duplicate node ID",
        ),
        (
            FlowNetwork(
                (Node("u", 0), Node("v", 0)),
                (
                    Edge("same", "u", "v", 1, 0),
                    Edge("same", "v", "u", 1, 0),
                ),
            ),
            "Duplicate edge ID",
        ),
        (
            FlowNetwork(
                (Node("u", 0),),
                (Edge("line", "u", "missing", 1, 0),),
            ),
            "Unknown target node 'missing' on edge 'line'",
        ),
        (
            FlowNetwork((Node("source", 2), Node("city", -1)), ()),
            "sum to zero",
        ),
        (
            FlowNetwork(
                (Node("u", 0), Node("v", 0)),
                (Edge("line", "u", "v", -1, 0),),
            ),
            "capacity",
        ),
        (
            FlowNetwork(
                (Node("u", 0), Node("v", 0)),
                (Edge("line", "u", "v", 1, 0, -1),),
            ),
            "lower_capacity",
        ),
        (
            FlowNetwork(
                (Node("u", 0), Node("v", 0)),
                (Edge("line", "u", "v", 1, 0, 2),),
            ),
            "exceeds capacity",
        ),
    )
    for network, expected_error in invalid_networks:
        with pytest.raises(ValueError, match=expected_error):
            validate_network(network)


def test_t11_rejects_float_boolean_and_string_numbers() -> None:
    network = primary_network()
    for invalid_value in (1.5, True, "1"):
        invalid_models = (
            replace(
                network,
                nodes=(
                    replace(network.nodes[0], balance=invalid_value),
                    network.nodes[1],
                ),
            ),
            replace(
                network,
                edges=(
                    replace(network.edges[0], capacity=invalid_value),
                    network.edges[1],
                ),
            ),
            replace(
                network,
                edges=(
                    replace(network.edges[0], unit_cost=invalid_value),
                    network.edges[1],
                ),
            ),
            replace(
                network,
                edges=(
                    replace(network.edges[0], lower_capacity=invalid_value),
                    network.edges[1],
                ),
            ),
        )
        for invalid_network in invalid_models:
            with pytest.raises(ValueError, match="must be an integer"):
                validate_network(invalid_network)

        with pytest.raises(ValueError, match="flow must be an integer"):
            validate_flow(network, {"line_a": invalid_value, "line_b": 5})


def test_t12_transit_fixture() -> None:
    result = evaluate_flow(
        load_network(EXAMPLES / "transit_network.json"),
        load_flow(EXAMPLES / "transit_flow.json"),
    )
    assert result.total_cost == 20
    assert result.net_outflow == {"source": 4, "junction": 0, "city": -4}


def test_t13_t14_lower_bound_and_signed_cost() -> None:
    lower_bound_network = replace(
        primary_network(),
        edges=(
            Edge("line_a", "source", "city", 5, 1, lower_capacity=2),
            Edge("line_b", "source", "city", 5, 4),
        ),
    )
    with pytest.raises(ValueError, match="below lower_capacity 2"):
        evaluate_flow(lower_bound_network, {"line_a": 1, "line_b": 5})
    assert (
        evaluate_flow(
            lower_bound_network,
            {"line_a": 2, "line_b": 4},
        ).total_cost
        == 18
    )

    signed_cost_network = replace(
        primary_network(),
        edges=(
            Edge("line_a", "source", "city", 5, -1),
            Edge("line_b", "source", "city", 5, 4),
        ),
    )
    result = evaluate_flow(signed_cost_network, {"line_a": 5, "line_b": 1})
    assert result.total_cost == -1


def test_t15_t16_parallel_and_opposite_edges_are_independent() -> None:
    parallel = primary_network()
    assert [edge.id for edge in parallel.edges] == ["line_a", "line_b"]
    assert evaluate_flow(parallel, {"line_a": 5, "line_b": 1}).total_cost == 9

    opposite = FlowNetwork(
        (Node("u", 3), Node("v", -3)),
        (
            Edge("forward", "u", "v", 5, 2),
            Edge("return", "v", "u", 2, 1),
        ),
    )
    result = evaluate_flow(opposite, {"forward": 4, "return": 1})
    assert result.total_cost == 9
    assert result.net_outflow == {"u": 3, "v": -3}


def test_t17_balanced_network_does_not_guarantee_a_feasible_candidate() -> None:
    network = FlowNetwork(
        (Node("source", 6), Node("city", -6)),
        (Edge("line", "source", "city", 5, 1),),
    )
    assert validate_network(network) is None
    with pytest.raises(ValueError, match="expected net outflow 6, received 5"):
        evaluate_flow(network, {"line": 5})


def test_t18_t19_empty_edges_isolated_nodes_and_rejected_shapes() -> None:
    result = evaluate_flow(FlowNetwork((Node("inactive", 0),), ()), {})
    assert result.total_cost == 0
    assert result.net_outflow == {"inactive": 0}

    zero_capacity = FlowNetwork(
        (Node("u", 0), Node("v", 0), Node("isolated", 0)),
        (Edge("zero", "u", "v", 0, 0),),
    )
    assert evaluate_flow(zero_capacity, {"zero": 0}).total_cost == 0

    invalid_networks = (
        FlowNetwork((), ()),
        FlowNetwork(
            (Node("u", 0),),
            (Edge("loop", "u", "u", 0, 0),),
        ),
    )
    for network in invalid_networks:
        with pytest.raises(ValueError):
            validate_network(network)


def test_t20_strict_json_loading(tmp_path: Path) -> None:
    invalid_json_cases = (
        ([], "must be an object"),
        ({"nodes": []}, "missing required field"),
        ({"nodes": [], "edges": [], "extra": 1}, "unexpected field"),
        (
            {"nodes": [{"id": 1, "balance": 0}], "edges": []},
            "Node ID must be a nonempty string",
        ),
    )
    for index, (value, expected_error) in enumerate(invalid_json_cases):
        path = write_json(tmp_path / f"invalid-{index}.json", value)
        with pytest.raises(ValueError, match=expected_error):
            load_network(path)

    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"nodes": [}', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_network(malformed)
    with pytest.raises(OSError):
        load_network(tmp_path / "missing.json")
    with pytest.raises(ValueError, match="Flow JSON must be an object"):
        load_flow(write_json(tmp_path / "flow.json", [1, 2]))


def test_t21_results_are_order_independent_without_input_mutation() -> None:
    network = primary_network()
    first_flow = {"line_a": 5, "line_b": 1}
    second_flow = {"line_b": 1, "line_a": 5}
    nodes_before = network.nodes
    edges_before = network.edges
    first_before = first_flow.copy()
    second_before = second_flow.copy()

    assert evaluate_flow(network, first_flow) == evaluate_flow(network, second_flow)
    assert network.nodes == nodes_before
    assert network.edges == edges_before
    assert first_flow == first_before
    assert second_flow == second_before
