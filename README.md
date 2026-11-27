# Renewable-Energy Routing

Project 6 for the Advanced Algorithms course, Master of Computer Science.

Build a regional microgrid routing model that meets electricity demand at minimum cost while respecting generation and transmission capacities. The project combines network-flow algorithms, GIS-based link selection, and geospatial representation learning.

## Status

Stage 1 is implemented: the package loads and validates fixed-balance flow
networks, validates a caller-supplied candidate flow, and evaluates its cost.
It does not search for a feasible or optimal flow.

## Project Documentation

- [Stage 00: Repository Foundation and Agent Guardrails](docs/stage_00_repository_foundation.md)
- [Stage 01: Problem Definition and Validation](docs/stage_01_problem_definition.md)

## Development Roadmap

### Stage 1: Problem Definition

- Document the network inputs, outputs, objective, and constraints.
- Define a small example with known feasible and optimal solutions.

### Stage 2: Maximum-Flow Foundations

- Implement residual networks, forward/reverse edges, and flow updates.
- Implement Ford-Fulkerson and Edmonds-Karp.
- Test capacity constraints, flow conservation, rerouting, and maximum-flow/minimum-cut agreement.

These methods solve maximum flow. They do **not** count toward the assignment's two required classical minimum-cost-flow methods.

### Later Milestones

- **Minimum-cost flow:** Implement at least two classical methods and a simplified minimum-ratio-cycle-driven cycle-canceling method. Check correctness against a reference solver and compare runtime as the edge count grows.
- **Theory:** Write a proof outline of Paper 1's reduction from minimum-cost flow to repeated minimum-ratio-cycle computations.
- **Spatial queries:** Construct candidate links using PostGIS-backed spatial queries; compare with a grid or geohash baseline as the search radius changes.
- **Geospatial learning:** Choose one representation technique to estimate demand or generation capacity. Compare against a simple baseline and evaluate the effect on routing cost and demand served.
- **Integration and defense:** Combine the components, demonstrate rerouting after a generation-site outage, and report unmet demand when full service is infeasible.

The cycle-based implementation demonstrates the underlying principle on small graphs. It does not reproduce the full almost-linear-time algorithm or inherit its runtime guarantee.

## Planned Structure

```text
src/          # Algorithms and integration code
examples/     # Small, manually verifiable examples
tests/       # Correctness and regression tests
benchmarks/   # Runtime and spatial-query experiments
data/         # Local datasets and data documentation
docs/         # Model definitions, proof outlines, and report notes
```

Directories will be added as needed. Each algorithm will have its own module and tests.

## Initial Setup

Use Python 3.10 for the initial implementation.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

On Windows:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Stage 1 runtime code uses only the Python standard library. The development
requirements install `pytest`.

## Stage 1 Usage

Run every Stage 1 data case with its expected result and a short explanation:

```bash
python examples/stage1/run_cases.py
```

This is the simplest command for rerunning the Stage 1 concept. It demonstrates
the two feasible two-link candidates, both rejected candidates, and the transit
candidate. To evaluate one supplied candidate directly:

```bash
python -m renewable_routing.stage1 \
  examples/stage1/two_link_network.json \
  examples/stage1/flow_optimal.json
```

The runner reports whether this candidate is feasible and, if so, its cost.
It explicitly does not check optimality.

Each implemented stage keeps its demonstration data under `examples/stageN/`
and its end-to-end example check under `tests/stageN/`. Detailed contract tests
remain available for implementation verification but are not needed for a
normal concept demonstration. Run all verification tests with:

```bash
python -m pytest -q
```

## Study Materials

- **Lecture 7:** Maximum flow, residual networks, and correctness proofs. Stage 2 focuses on PDF pages 128-142 and 150-155.
- **Lecture 6:** Computational geometry and spatial-search foundations.
- **Paper 1:** Chen et al. (2025), *Maximum Flow and Minimum-Cost Flow in Almost-Linear Time*.
- **Paper 2:** Liu et al. (2025), *Representation Learning for Geospatial Data*.

## Modeling Scope

The microgrid is modeled as a network-flow problem, not a full electrical power-flow simulation. All data assumptions, units, and simplifications will be documented.
