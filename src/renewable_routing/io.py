"""Strict JSON loading for Stage 1 networks and candidate flows."""

import json
from pathlib import Path
from typing import Any

from .models import Edge, FlowNetwork, Node
from .validation import validate_network


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as input_file:
        return json.load(input_file, object_pairs_hook=_reject_duplicate_keys)


def _check_fields(
    record: dict[str, Any],
    required: set[str],
    optional: set[str],
    description: str,
) -> None:
    fields = set(record)
    missing = sorted(required - fields)
    if missing:
        raise ValueError(f"{description} is missing required field '{missing[0]}'")

    unexpected = sorted(fields - required - optional)
    if unexpected:
        raise ValueError(f"{description} has unexpected field '{unexpected[0]}'")


def load_network(path: str | Path) -> FlowNetwork:
    """Load and structurally validate a network from its exact JSON schema."""

    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Network JSON must be an object")
    _check_fields(data, {"nodes", "edges"}, set(), "Network JSON")

    node_records = data["nodes"]
    edge_records = data["edges"]
    if not isinstance(node_records, list):
        raise ValueError("Network field 'nodes' must be an array")
    if not isinstance(edge_records, list):
        raise ValueError("Network field 'edges' must be an array")

    nodes: list[Node] = []
    for index, record in enumerate(node_records):
        description = f"Node record at index {index}"
        if not isinstance(record, dict):
            raise ValueError(f"{description} must be an object")
        _check_fields(record, {"id", "balance"}, set(), description)
        nodes.append(Node(id=record["id"], balance=record["balance"]))

    edges: list[Edge] = []
    for index, record in enumerate(edge_records):
        description = f"Edge record at index {index}"
        if not isinstance(record, dict):
            raise ValueError(f"{description} must be an object")
        _check_fields(
            record,
            {"id", "source", "target", "capacity", "unit_cost"},
            {"lower_capacity"},
            description,
        )
        edges.append(
            Edge(
                id=record["id"],
                source=record["source"],
                target=record["target"],
                capacity=record["capacity"],
                unit_cost=record["unit_cost"],
                lower_capacity=record.get("lower_capacity", 0),
            )
        )

    network = FlowNetwork(nodes=tuple(nodes), edges=tuple(edges))
    validate_network(network)
    return network


def load_flow(path: str | Path) -> dict[str, int]:
    """Load a candidate edge-ID-to-integer mapping from JSON."""

    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Flow JSON must be an object mapping edge IDs to integers")

    for edge_id, value in data.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"Flow for edge '{edge_id}' must be an integer, received {value!r}"
            )
    return data
