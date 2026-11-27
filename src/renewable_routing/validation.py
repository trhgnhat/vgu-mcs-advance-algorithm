"""Structural and candidate-flow validation."""

from collections.abc import Mapping

from .models import FlowNetwork


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_identifier(value: object, description: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{description} must be a nonempty string")


def validate_network(network: FlowNetwork) -> None:
    """Validate the structure and numerical fields of a flow network."""

    if not network.nodes:
        raise ValueError("A network must contain at least one node")

    node_ids: set[str] = set()
    for node in network.nodes:
        _validate_identifier(node.id, "Node ID")
        if node.id in node_ids:
            raise ValueError(f"Duplicate node ID: {node.id}")
        node_ids.add(node.id)

        if not _is_integer(node.balance):
            raise ValueError(
                f"Node '{node.id}': balance must be an integer, "
                f"received {node.balance!r}"
            )

    edge_ids: set[str] = set()
    for edge in network.edges:
        _validate_identifier(edge.id, "Edge ID")
        if edge.id in edge_ids:
            raise ValueError(f"Duplicate edge ID: {edge.id}")
        edge_ids.add(edge.id)

        _validate_identifier(edge.source, f"Source on edge '{edge.id}'")
        _validate_identifier(edge.target, f"Target on edge '{edge.id}'")
        if edge.source not in node_ids:
            raise ValueError(
                f"Unknown source node '{edge.source}' on edge '{edge.id}'"
            )
        if edge.target not in node_ids:
            raise ValueError(
                f"Unknown target node '{edge.target}' on edge '{edge.id}'"
            )
        if edge.source == edge.target:
            raise ValueError(f"Self-loop is not allowed on edge '{edge.id}'")

        for field_name, value in (
            ("capacity", edge.capacity),
            ("unit_cost", edge.unit_cost),
            ("lower_capacity", edge.lower_capacity),
        ):
            if not _is_integer(value):
                raise ValueError(
                    f"Edge '{edge.id}': {field_name} must be an integer, "
                    f"received {value!r}"
                )

        if edge.lower_capacity < 0:
            raise ValueError(
                f"Edge '{edge.id}': lower_capacity "
                f"{edge.lower_capacity} must be nonnegative"
            )
        if edge.capacity < 0:
            raise ValueError(
                f"Edge '{edge.id}': capacity {edge.capacity} must be nonnegative"
            )
        if edge.lower_capacity > edge.capacity:
            raise ValueError(
                f"Edge '{edge.id}': lower_capacity {edge.lower_capacity} "
                f"exceeds capacity {edge.capacity}"
            )

    total_balance = sum(node.balance for node in network.nodes)
    if total_balance != 0:
        raise ValueError(f"Node balances must sum to zero, received {total_balance}")


def _calculate_net_outflow(
    network: FlowNetwork,
    flow: Mapping[str, int],
) -> dict[str, int]:
    # Each original edge contributes positively at its tail and negatively
    # at its head, including parallel and opposite-direction edges.
    net_outflow = {node.id: 0 for node in network.nodes}
    for edge in network.edges:
        edge_flow = flow[edge.id]
        net_outflow[edge.source] += edge_flow
        net_outflow[edge.target] -= edge_flow
    return net_outflow


def validate_flow(
    network: FlowNetwork,
    flow: Mapping[str, int],
) -> None:
    """Validate a complete candidate flow without searching for another one."""

    validate_network(network)
    if not isinstance(flow, Mapping):
        raise ValueError("Candidate flow must be a mapping from edge IDs to integers")

    edge_by_id = {edge.id: edge for edge in network.edges}
    missing_ids = [edge.id for edge in network.edges if edge.id not in flow]
    if missing_ids:
        raise ValueError(f"Missing flow ID: {missing_ids[0]}")

    unknown_ids = [edge_id for edge_id in flow if edge_id not in edge_by_id]
    if unknown_ids:
        raise ValueError(f"Unknown flow ID: {unknown_ids[0]}")

    for edge in network.edges:
        edge_flow = flow[edge.id]
        if not _is_integer(edge_flow):
            raise ValueError(
                f"Edge '{edge.id}': flow must be an integer, "
                f"received {edge_flow!r}"
            )
        if edge_flow < edge.lower_capacity:
            raise ValueError(
                f"Edge '{edge.id}': flow {edge_flow} is below lower_capacity "
                f"{edge.lower_capacity}"
            )
        if edge_flow > edge.capacity:
            raise ValueError(
                f"Edge '{edge.id}': flow {edge_flow} exceeds capacity "
                f"{edge.capacity}"
            )

    net_outflow = _calculate_net_outflow(network, flow)
    for node in network.nodes:
        actual = net_outflow[node.id]
        if actual != node.balance:
            raise ValueError(
                f"Node '{node.id}': expected net outflow {node.balance}, "
                f"received {actual}"
            )
