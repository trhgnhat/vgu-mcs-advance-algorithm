"""Maximum-flow problem, result, and certificate validation."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from .models import FlowNetwork
from .validation import validate_network


AlgorithmName = Literal["ford_fulkerson", "edmonds_karp"]


@dataclass(frozen=True)
class MaxFlowProblem:
    """A zero-balance capacity network with explicit terminals."""

    network: FlowNetwork
    source: str
    sink: str


@dataclass(frozen=True)
class MaxFlowResult:
    """A maximum flow together with an equal-capacity cut certificate."""

    algorithm: AlgorithmName
    value: int
    flow: dict[str, int]
    source_side: frozenset[str]
    sink_side: frozenset[str]
    cut_capacity: int
    augmentations: int


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _net_outflows(
    problem: MaxFlowProblem, flow: Mapping[str, int]
) -> dict[str, int]:
    net = {node.id: 0 for node in problem.network.nodes}
    for edge in problem.network.edges:
        edge_flow = flow[edge.id]
        net[edge.source] += edge_flow
        net[edge.target] -= edge_flow
    return net


def _calculate_cut_capacity(
    problem: MaxFlowProblem, source_side: frozenset[str]
) -> int:
    return sum(
        edge.capacity
        for edge in problem.network.edges
        if edge.source in source_side and edge.target not in source_side
    )


def validate_max_flow_problem(problem: MaxFlowProblem) -> None:
    """Validate the Stage 2 wrapper and its supported network subset."""

    if not isinstance(problem, MaxFlowProblem):
        raise ValueError("Maximum-flow problem must be a MaxFlowProblem")

    validate_network(problem.network)
    node_ids = {node.id for node in problem.network.nodes}

    if not isinstance(problem.source, str):
        raise ValueError("Maximum-flow source must be a string")
    if not isinstance(problem.sink, str):
        raise ValueError("Maximum-flow sink must be a string")
    if problem.source not in node_ids:
        raise ValueError(f"Unknown source node '{problem.source}'")
    if problem.sink not in node_ids:
        raise ValueError(f"Unknown sink node '{problem.sink}'")
    if problem.source == problem.sink:
        raise ValueError("Maximum-flow source and sink must be distinct")

    for node in problem.network.nodes:
        if node.balance != 0:
            raise ValueError(
                f"Node '{node.id}': maximum-flow balance must be 0, "
                f"received {node.balance}"
            )

    for edge in problem.network.edges:
        if edge.lower_capacity != 0:
            raise ValueError(
                f"Edge '{edge.id}': maximum-flow lower_capacity must be 0, "
                f"received {edge.lower_capacity}"
            )
        if edge.unit_cost != 0:
            raise ValueError(
                f"Edge '{edge.id}': maximum-flow unit_cost must be 0, "
                f"received {edge.unit_cost}"
            )
        if edge.target == problem.source:
            raise ValueError(
                f"Edge '{edge.id}' enters source '{problem.source}'"
            )
        if edge.source == problem.sink:
            raise ValueError(f"Edge '{edge.id}' leaves sink '{problem.sink}'")


def validate_max_flow(
    problem: MaxFlowProblem, flow: Mapping[str, int]
) -> int:
    """Validate a complete feasible state and return its source value."""

    validate_max_flow_problem(problem)
    if not isinstance(flow, Mapping):
        raise ValueError("Maximum flow must be a mapping from edge IDs to integers")

    edge_by_id = {edge.id: edge for edge in problem.network.edges}
    missing_ids = [edge.id for edge in problem.network.edges if edge.id not in flow]
    if missing_ids:
        raise ValueError(f"Missing flow ID: {missing_ids[0]}")
    unknown_ids = [edge_id for edge_id in flow if edge_id not in edge_by_id]
    if unknown_ids:
        raise ValueError(f"Unknown flow ID: {unknown_ids[0]}")

    for edge in problem.network.edges:
        edge_flow = flow[edge.id]
        if not _is_integer(edge_flow):
            raise ValueError(
                f"Edge '{edge.id}': flow must be an integer, "
                f"received {edge_flow!r}"
            )
        if edge_flow < 0:
            raise ValueError(
                f"Edge '{edge.id}': flow {edge_flow} must be nonnegative"
            )
        if edge_flow > edge.capacity:
            raise ValueError(
                f"Edge '{edge.id}': flow {edge_flow} exceeds capacity "
                f"{edge.capacity}"
            )

    net = _net_outflows(problem, flow)
    for node in problem.network.nodes:
        if node.id not in (problem.source, problem.sink) and net[node.id] != 0:
            raise ValueError(
                f"Node '{node.id}': expected net outflow 0, "
                f"received {net[node.id]}"
            )

    value = net[problem.source]
    if value < 0:
        raise ValueError(
            f"Source '{problem.source}': flow value must be nonnegative, "
            f"received {value}"
        )
    if net[problem.sink] != -value:
        raise ValueError(
            f"Sink '{problem.sink}': expected net outflow {-value}, "
            f"received {net[problem.sink]}"
        )
    return value


def validate_max_flow_result(
    problem: MaxFlowProblem, result: MaxFlowResult
) -> None:
    """Independently validate a feasible flow and equal-capacity cut."""

    validate_max_flow_problem(problem)
    if not isinstance(result, MaxFlowResult):
        raise ValueError("Maximum-flow result must be a MaxFlowResult")
    if result.algorithm not in ("ford_fulkerson", "edmonds_karp"):
        raise ValueError(f"Unknown maximum-flow algorithm: {result.algorithm!r}")

    for field_name, value in (
        ("value", result.value),
        ("cut_capacity", result.cut_capacity),
        ("augmentations", result.augmentations),
    ):
        if not _is_integer(value):
            raise ValueError(
                f"Result {field_name} must be an integer, received {value!r}"
            )
    if result.value < 0:
        raise ValueError("Result value must be nonnegative")
    if result.cut_capacity < 0:
        raise ValueError("Result cut_capacity must be nonnegative")
    if result.augmentations < 0:
        raise ValueError("Result augmentations must be nonnegative")
    if not isinstance(result.flow, dict):
        raise ValueError("Result flow must be a dictionary")
    if not isinstance(result.source_side, frozenset):
        raise ValueError("Result source_side must be a frozenset")
    if not isinstance(result.sink_side, frozenset):
        raise ValueError("Result sink_side must be a frozenset")

    node_ids = {node.id for node in problem.network.nodes}
    if result.source_side & result.sink_side:
        raise ValueError("Result cut sides must be disjoint")
    if result.source_side | result.sink_side != node_ids:
        raise ValueError("Result cut sides must partition every network node")
    if problem.source not in result.source_side:
        raise ValueError("Result source_side must contain the source")
    if problem.sink not in result.sink_side:
        raise ValueError("Result sink_side must contain the sink")

    actual_value = validate_max_flow(problem, result.flow)
    if result.value != actual_value:
        raise ValueError(
            f"Result value {result.value} does not match flow value {actual_value}"
        )

    actual_cut_capacity = _calculate_cut_capacity(problem, result.source_side)
    if result.cut_capacity != actual_cut_capacity:
        raise ValueError(
            f"Result cut_capacity {result.cut_capacity} does not match "
            f"original-edge cut capacity {actual_cut_capacity}"
        )
    if result.value != result.cut_capacity:
        raise ValueError(
            f"Flow value {result.value} does not equal cut capacity "
            f"{result.cut_capacity}"
        )
