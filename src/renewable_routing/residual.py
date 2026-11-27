"""Residual-network snapshots and safe maximum-flow augmentation."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from .max_flow import MaxFlowProblem, validate_max_flow


@dataclass(frozen=True)
class ResidualArc:
    """One forward or reverse residual option for an original edge."""

    edge_id: str
    source: str
    target: str
    direction: Literal[1, -1]
    residual_capacity: int


ResidualGraph = dict[str, tuple[ResidualArc, ...]]


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def build_residual(
    problem: MaxFlowProblem, flow: Mapping[str, int]
) -> ResidualGraph:
    """Build a fresh deterministic residual snapshot."""

    validate_max_flow(problem, flow)
    adjacency: dict[str, list[ResidualArc]] = {
        node.id: [] for node in problem.network.nodes
    }

    for edge in problem.network.edges:
        edge_flow = flow[edge.id]
        forward_capacity = edge.capacity - edge_flow
        if forward_capacity > 0:
            adjacency[edge.source].append(
                ResidualArc(
                    edge_id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    direction=1,
                    residual_capacity=forward_capacity,
                )
            )
        if edge_flow > 0:
            adjacency[edge.target].append(
                ResidualArc(
                    edge_id=edge.id,
                    source=edge.target,
                    target=edge.source,
                    direction=-1,
                    residual_capacity=edge_flow,
                )
            )

    return {node_id: tuple(arcs) for node_id, arcs in adjacency.items()}


def augment_flow(
    problem: MaxFlowProblem,
    flow: Mapping[str, int],
    path: tuple[ResidualArc, ...],
) -> tuple[dict[str, int], int]:
    """Apply one current, simple source-to-sink residual path."""

    old_value = validate_max_flow(problem, flow)
    if not isinstance(path, tuple):
        raise ValueError("Residual path must be a tuple of arcs")
    if not path:
        raise ValueError("Residual path must not be empty")

    edge_by_id = {edge.id: edge for edge in problem.network.edges}
    current_capacities: list[int] = []
    expected_source = problem.source
    visited = {problem.source}

    # Validate the complete path before copying or changing the flow.
    for index, arc in enumerate(path):
        if not isinstance(arc, ResidualArc):
            raise ValueError(f"Residual path item {index} must be a ResidualArc")
        if arc.edge_id not in edge_by_id:
            raise ValueError(f"Unknown original edge '{arc.edge_id}' in residual path")
        if not _is_integer(arc.direction) or arc.direction not in (1, -1):
            raise ValueError(
                f"Residual arc for edge '{arc.edge_id}' has invalid direction "
                f"{arc.direction!r}"
            )
        if not _is_integer(arc.residual_capacity):
            raise ValueError(
                f"Residual arc for edge '{arc.edge_id}' must have an integer "
                "capacity"
            )
        if arc.residual_capacity <= 0:
            raise ValueError(
                f"Residual arc for edge '{arc.edge_id}' must have positive capacity"
            )
        if arc.source != expected_source:
            raise ValueError(
                f"Residual path is disconnected before edge '{arc.edge_id}'"
            )

        edge = edge_by_id[arc.edge_id]
        if arc.direction == 1:
            expected_endpoints = (edge.source, edge.target)
            current_capacity = edge.capacity - flow[edge.id]
        else:
            expected_endpoints = (edge.target, edge.source)
            current_capacity = flow[edge.id]
        if (arc.source, arc.target) != expected_endpoints:
            raise ValueError(
                f"Residual arc endpoints for edge '{arc.edge_id}' do not match "
                f"direction {arc.direction}"
            )
        if arc.residual_capacity != current_capacity:
            raise ValueError(
                f"Residual arc for edge '{arc.edge_id}' is stale: snapshot "
                f"{arc.residual_capacity}, current {current_capacity}"
            )
        if arc.target in visited:
            raise ValueError(
                f"Residual path repeats vertex '{arc.target}'"
            )

        current_capacities.append(current_capacity)
        visited.add(arc.target)
        expected_source = arc.target

    if expected_source != problem.sink:
        raise ValueError(
            f"Residual path must end at sink '{problem.sink}', "
            f"received '{expected_source}'"
        )

    delta = min(current_capacities)
    new_flow = dict(flow)
    for arc in path:
        new_flow[arc.edge_id] += arc.direction * delta

    new_value = validate_max_flow(problem, new_flow)
    if new_value != old_value + delta:
        raise ValueError(
            f"Residual augmentation should increase value by {delta}, "
            f"received increase {new_value - old_value}"
        )
    return new_flow, delta


def reachable_vertices(
    residual: ResidualGraph, source: str
) -> frozenset[str]:
    """Return vertices reachable through positive residual arcs."""

    if not isinstance(residual, dict):
        raise ValueError("Residual graph must be a dictionary")
    if source not in residual:
        raise ValueError(f"Unknown residual source node '{source}'")

    reached = {source}
    stack = [source]
    while stack:
        node = stack.pop()
        for arc in residual[node]:
            if arc.residual_capacity <= 0:
                continue
            if arc.target not in residual:
                raise ValueError(
                    f"Residual arc targets unknown node '{arc.target}'"
                )
            if arc.target not in reached:
                reached.add(arc.target)
                stack.append(arc.target)
    return frozenset(reached)
