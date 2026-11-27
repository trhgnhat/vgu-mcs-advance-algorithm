"""Edmonds-Karp maximum flow using deterministic breadth-first search."""

from collections import deque

from .max_flow import (
    MaxFlowProblem,
    MaxFlowResult,
    _calculate_cut_capacity,
    validate_max_flow_problem,
    validate_max_flow_result,
)
from .residual import (
    ResidualArc,
    ResidualGraph,
    augment_flow,
    build_residual,
    reachable_vertices,
)


def _validate_search_terminals(
    residual: ResidualGraph, source: str, sink: str
) -> None:
    if source not in residual:
        raise ValueError(f"Unknown residual source node '{source}'")
    if sink not in residual:
        raise ValueError(f"Unknown residual sink node '{sink}'")
    if source == sink:
        raise ValueError("Residual source and sink must be distinct")


def _reconstruct_path(
    parent: dict[str, ResidualArc], source: str, sink: str
) -> tuple[ResidualArc, ...]:
    reversed_path: list[ResidualArc] = []
    node = sink
    while node != source:
        arc = parent[node]
        reversed_path.append(arc)
        node = arc.source
    reversed_path.reverse()
    return tuple(reversed_path)


def find_path_bfs(
    residual: ResidualGraph, source: str, sink: str
) -> tuple[ResidualArc, ...] | None:
    """Find a fewest-edge residual path in stored adjacency order."""

    _validate_search_terminals(residual, source, sink)
    queue = deque([source])
    visited = {source}
    parent: dict[str, ResidualArc] = {}

    while queue:
        node = queue.popleft()
        for arc in residual[node]:
            if arc.target in visited:
                continue
            visited.add(arc.target)
            parent[arc.target] = arc
            if arc.target == sink:
                return _reconstruct_path(parent, source, sink)
            queue.append(arc.target)

    return None


def solve_edmonds_karp(problem: MaxFlowProblem) -> MaxFlowResult:
    """Solve maximum flow from zero using BFS augmenting paths."""

    validate_max_flow_problem(problem)
    flow = {edge.id: 0 for edge in problem.network.edges}
    augmentations = 0

    while True:
        residual = build_residual(problem, flow)
        path = find_path_bfs(residual, problem.source, problem.sink)
        if path is None:
            break
        flow, _ = augment_flow(problem, flow, path)
        augmentations += 1

    source_side = reachable_vertices(residual, problem.source)
    all_nodes = frozenset(node.id for node in problem.network.nodes)
    sink_side = all_nodes - source_side
    result = MaxFlowResult(
        algorithm="edmonds_karp",
        value=sum(
            flow[edge.id]
            for edge in problem.network.edges
            if edge.source == problem.source
        ),
        flow=dict(flow),
        source_side=source_side,
        sink_side=sink_side,
        cut_capacity=_calculate_cut_capacity(problem, source_side),
        augmentations=augmentations,
    )
    validate_max_flow_result(problem, result)
    return result
