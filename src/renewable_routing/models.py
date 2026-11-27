"""Data models for fixed-balance flow networks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    """A network node with a required net outflow."""

    id: str
    balance: int


@dataclass(frozen=True)
class Edge:
    """A directed original edge with flow bounds and a per-unit cost."""

    id: str
    source: str
    target: str
    capacity: int
    unit_cost: int
    lower_capacity: int = 0


@dataclass(frozen=True)
class FlowNetwork:
    """An immutable collection of nodes and original directed edges."""

    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]


@dataclass
class FlowEvaluation:
    """The cost and node net outflows of a feasible candidate flow."""

    total_cost: int
    net_outflow: dict[str, int]
