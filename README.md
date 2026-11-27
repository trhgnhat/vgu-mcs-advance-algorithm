# Renewable-Energy Routing

Project 6 for the Advanced Algorithms course, Master of Computer Science.

Build a regional microgrid routing model that meets electricity demand at minimum cost while respecting generation and transmission capacities. The project combines network-flow algorithms, GIS-based link selection, and geospatial representation learning.

## Status

Stages 1 and 2 are implemented. Stage 1 validates and evaluates a supplied
fixed-balance flow. Stage 2 finds maximum flow with Ford-Fulkerson or
Edmonds-Karp and returns an equal-capacity cut certificate. Neither stage
optimizes routing cost.

## Stage Table of Contents

| Stage | Topic | Status |
|---|---|---|
| 00 | [Repository Foundation and Agent Guardrails](docs/stage_00_repository_foundation.md) | ✅ Finished |
| 01 | [Problem Definition and Validation](docs/stage_01_problem_definition.md) | ✅ Finished |
| 02 | [Maximum-Flow Foundations](docs/stage_02_maximum_flow_foundations.md) ([proof notes](docs/stage_02_proof_notes.md)) | ✅ Finished |
| 03 | First Classical Minimum-Cost-Flow Solver (Successive Shortest Paths) | (pending) |
| 04 | Second Classical Minimum-Cost-Flow Solver | (pending) |
| 05 | Simplified Minimum-Ratio-Cycle Method | (pending) |
| 06 | Paper 1 Proof Outline and Engine Checkpoint | (pending) |
| 07 | Solver Benchmarking and Scaling | (pending) |
| 08 | GIS Data and Regional Microgrid Model | (pending) |
| 09 | PostGIS Spatial Indexing and Baseline Comparison | (pending) |
| 10 | Geospatial Representation and Demand/Capacity Estimation | (pending) |
| 11 | Integrated Optimizer and Outage Rerouting | (pending) |
| 12 | Technical Paper, Reproducibility, and Defense Preparation | (pending) |

Stages 03-12 are roadmap targets, not approved implementation contracts. Define
and review each stage specification before implementation. The detailed roadmap
is available in [Project Roadmap](docs/PROJECT_ROADMAP.md).

Ford-Fulkerson and Edmonds-Karp solve maximum flow; they do **not** count as the
assignment's two required classical minimum-cost-flow methods.

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

Stage 1 and Stage 2 runtime code use only the Python standard library. The
development requirements install `pytest`.

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

## Stage 2 Usage

Run all Stage 2 fixtures with both algorithms:

```bash
python examples/stage2/run_cases.py
```

Run one solver and inspect its flow/cut certificate:

```bash
python -m renewable_routing.stage2 \
  examples/stage2/rerouting.json \
  --source s \
  --sink t \
  --algorithm ford-fulkerson
```

Use `--algorithm edmonds-karp` for BFS path selection. Stage 2 starts from zero
flow and supports only zero node balances, zero lower capacities, and zero
costs. It rejects unsupported fields instead of ignoring them.

## Study Materials

- **Lecture 7:** Maximum flow, residual networks, and correctness proofs. Stage 2 focuses on PDF pages 128-142 and 150-155.
- **Lecture 6:** Computational geometry and spatial-search foundations.
- **Paper 1:** Chen et al. (2025), *Maximum Flow and Minimum-Cost Flow in Almost-Linear Time*.
- **Paper 2:** Liu et al. (2025), *Representation Learning for Geospatial Data*.

## Modeling Scope

The microgrid is modeled as a network-flow problem, not a full electrical power-flow simulation. All data assumptions, units, and simplifications will be documented.
