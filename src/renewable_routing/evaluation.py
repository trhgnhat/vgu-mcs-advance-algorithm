"""Evaluation of explicitly supplied candidate flows."""

from collections.abc import Mapping

from .models import FlowEvaluation, FlowNetwork
from .validation import _calculate_net_outflow, validate_flow


def evaluate_flow(
    network: FlowNetwork,
    flow: Mapping[str, int],
) -> FlowEvaluation:
    """Validate a candidate and return its cost and node net outflows."""

    validate_flow(network, flow)
    total_cost = sum(edge.unit_cost * flow[edge.id] for edge in network.edges)
    return FlowEvaluation(
        total_cost=total_cost,
        net_outflow=_calculate_net_outflow(network, flow),
    )
