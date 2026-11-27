# Stage 02: Maximum-Flow Foundations

> **Project:** Renewable-Energy Routing - Project 6, Advanced Algorithms  
> **Repository location:** `docs/stage_02_maximum_flow_foundations.md`  
> **Target:** Python 3.10; `src/renewable_routing/`  
> **Status:** Proposed implementation contract, not evidence of implemented code or passing tests.  
> **Boundary:** Find a maximum flow and return a checkable cut certificate. Do not optimize cost.

## Contents

1. [Target and assignment connection](#1-target-and-assignment-connection)
2. [Scope and prerequisites](#2-scope-and-prerequisites)
3. [Exact lecture references](#3-exact-lecture-references)
4. [Maximum-flow contract](#4-maximum-flow-contract)
5. [Files and public APIs](#5-files-and-public-apis)
6. [Residual arcs and safe updates](#6-residual-arcs-and-safe-updates)
7. [Algorithms and proof obligations](#7-algorithms-and-proof-obligations)
8. [Fixtures and expected results](#8-fixtures-and-expected-results)
9. [CLI and JSON behavior](#9-cli-and-json-behavior)
10. [Required tests](#10-required-tests)
11. [Implementation order and acceptance](#11-implementation-order-and-acceptance)
12. [Short lecturer questions and answers](#12-short-lecturer-questions-and-answers)

## 1. Target and assignment connection

**Target:** Given a supported directed network, a source, and a sink, construct a maximum flow using either Ford-Fulkerson with DFS or Edmonds-Karp with BFS. Return the original-edge flows, flow value, and an original-network cut with equal capacity.

Stage 01 checks a caller-supplied fixed-balance flow. Stage 02 searches for a flow with maximum source-to-sink throughput. These are different contracts: preserve Stage 01's API and behavior rather than weakening its validator for this stage.

This stage establishes the residual-network and correctness foundations needed by later minimum-cost-flow implementations. Ford-Fulkerson and Edmonds-Karp do **not** satisfy the assignment's requirement for two classical minimum-cost-flow methods. Nor does this stage implement Paper 1's almost-linear algorithm.

Repository conventions and working procedures are inherited from [Stage 00](stage_00_repository_foundation.md), [AGENTS.md](../AGENTS.md), and the [project roadmap](PROJECT_ROADMAP.md). Do not repeat or replace those policies in code.

**Source versus design:** The flow method, residual capacities, and max-flow/min-cut proof come from Lecture 7. The wrapper model, zero-valued placeholders, API names, file layout, deterministic ordering, error behavior, and tests below are repository design choices. This document explicitly specifies them; they are not quotations from the lecture.

## 2. Scope and prerequisites

### In scope

- An explicit single-source/single-sink maximum-flow contract.
- Residual arcs that retain original-edge identity and direction.
- Deterministic DFS and BFS path selection.
- Bottleneck augmentation, including cancellation through reverse arcs.
- Two solver entrypoints, starting from zero flow.
- A flow-and-cut optimality certificate and its validator.
- Local fixtures, a CLI, proof notes, and regression tests.

### Out of scope

- Minimum-cost optimization, cost potentials, scaling, network simplex, and cycle canceling.
- Positive lower-bound transformations, prescribed source/sink throughput, and multiple-source modeling.
- Solver warm starts, outage recovery, GIS, databases, learning, and performance benchmarking.
- A general solver framework, external solver dependency, or full reproduction of Paper 1.

### Before implementation

Read the root agent instructions, Stage 00, [Stage 01](stage_01_problem_definition.md), and this file. Inspect the repository and actual Stage 01 test results. The conversation does not establish that Stage 01 was implemented.

Run the existing Stage 01 tests before changing shared code. If its package or public functions are missing, report that prerequisite rather than silently implementing an entire prior stage. Continue independent planning or documentation work where possible.

Runtime dependencies remain the standard library; tests use the existing `pytest` dependency. Do not download papers, datasets, or a reference solver. A test-only small-graph cut oracle is specified below instead.

## 3. Exact lecture references

Use the supplied `Uploaded_Lecture07_graph_theory_advanced.pdf`. Numbers in the first column are PDF viewer pages, not printed slide labels.

| PDF pages | Printed slides | What to extract for this stage |
|---|---|---|
| 123-127 | 113-117 | Flow, source/sink value, cuts, and the flow-versus-cut upper bound. |
| 128 | 118 | Forward and backward residual capacities. |
| 129-132 | 119 | Why forward-only routing gets stuck; the required rerouting example. |
| 133-134 | 120-121 | Bottleneck, feasible augmentation, and increase of flow value. |
| 135 | 122 | Ford-Fulkerson pseudocode. |
| 136-137 | 123-124 | Termination for integer capacities; capacity-dependent bound. |
| 138-142 | 125-129 | No augmenting path, reachable-set cut, and optimality certificate. |
| 150-155 | 134-139 | Edmonds-Karp, BFS distances, augmentation count, and complexity. |
| 156-159, 166, 168-169 | 140-143, 148, 150-151 | Six-node example with maximum flow and cut capacity 23. |

Lecture 6 and Paper 2 are not prerequisites for this stage. Do not read unrelated lecture sections before implementing these specific requirements.

The lecture's endpoint-based residual notation assumes no antiparallel original edges in its simple case; PDF page 133 discusses that assumption. Our representation preserves each original edge separately, including parallel and opposite-direction edges. An endpoint-membership test alone must not decide whether an arc is forward or reverse.

## 4. Maximum-flow contract

### 4.1 Reuse data without changing Stage 01

Introduce `MaxFlowProblem`, containing an existing `FlowNetwork` plus explicit `source` and `sink` IDs.

For this Stage 02 wrapper:

- Every `Node.balance` must equal `0`.
- Every `Edge.lower_capacity` must equal `0`.
- Every `Edge.unit_cost` must equal `0`.

These zeros make the stored network a capacity/topology input. Under the **maximum-flow wrapper**, terminal amounts are determined by the solver, not prescribed by `Node.balance`. At intermediate nodes, conservation still applies.

Do not pass a nonzero source-to-sink flow to Stage 01's `validate_flow` or `evaluate_flow`: those functions correctly enforce the stored fixed balances. Add separate maximum-flow validators instead.

Reject nonzero balances, positive lower bounds, and nonzero costs with useful messages. Do not erase or ignore them. The cost restriction prevents accidentally treating a cost-bearing Stage 01 instance as an optimized result; it is an initial repository restriction, not a mathematical limitation of maximum flow.

To compare with the two-link Stage 01 example, create a **new** Stage 02 fixture with zero balances and costs. Never edit the old fixture. Its maximum throughput is 10, not the Stage 01 prescribed demand of 6.

### 4.2 Supported topology and numbers

First apply Stage 01's `validate_network`, then enforce this wrapper's restrictions:

- Source and sink are existing, distinct node IDs; require strings.
- No original edge enters the source or leaves the sink, following the lecture's terminal convention. Reject such an edge even when its capacity is zero.
- Parallel and opposite-direction original edges between other permitted endpoints are supported independently.
- Capacities and flow values are integers, excluding booleans, with `0 <= flow <= capacity`.
- Self-loops remain rejected, consistent with Stage 01.
- Zero-capacity edges, isolated nodes, disconnected components, and an empty edge list are allowed.

Allowing nodes outside an `s`-to-`t` path is an explicit engineering relaxation of the definition on PDF page 123. A disconnected sink produces a valid maximum of zero, not an input error or an infeasibility claim. Since lower bounds are zero, zero flow is always a feasible start for supported input.

### 4.3 Feasible maximum-flow states

For each original edge, require an explicitly supplied integer flow under its unique ID, including zero. Reject missing and unknown IDs.

Let `net[v] = outflow(v) - inflow(v)`. Require:

```text
net[v] == 0                    for every v other than source and sink
value = net[source] >= 0
net[sink] == -value
0 <= flow[e.id] <= e.capacity   for every original edge
```

There is no constraint `value == source.balance`. Do not calculate value by summing all edge flows; multi-edge paths would be counted repeatedly.

### 4.4 Required result and certificate

Return the value, a complete original-edge flow mapping, the algorithm name, the augmentation count, and a cut partition `(source_side, sink_side)`.

After termination, construct `source_side` as the vertices reachable from the source through positive residual arcs. Let `sink_side` contain every other node, including any unreachable isolated nodes.

Compute cut capacity from **original edges**:

```text
cut_capacity = sum(
    edge.capacity
    for edge in network.edges
    if edge.source in source_side and edge.target in sink_side
)
```

Count every parallel edge separately. Do not count reverse residual arcs or original edges crossing from the sink side back to the source side.

A feasible flow plus a valid cut with `value == cut_capacity` certifies **maximum throughput**, not minimum cost. The verifier may accept any valid equal-capacity cut; it need not require a unique partition. The solvers themselves return the reachable-set construction.

## 5. Files and public APIs

### 5.1 New files

Keep all existing Stage 01 files and contracts intact. Add only the files needed here:

```text
src/renewable_routing/
  max_flow.py                 # Problem/result types, validators, cut-capacity check
  residual.py                 # Arc snapshots, construction, augmentation, reachability
  ford_fulkerson.py           # DFS path search and its solver
  edmonds_karp.py             # BFS path search and its solver
  stage2.py                   # Thin CLI, using the existing network JSON loader
examples/stage2/
  rerouting.json
  bottleneck.json
  parallel_edges.json
  opposite_edges.json
  disconnected.json
  lecture_23.json
tests/
  test_stage2_contract.py
  test_stage2_residual.py
  test_stage2_ford_fulkerson.py
  test_stage2_edmonds_karp.py
  test_stage2_certificate.py
  test_stage2_cli.py
docs/
  stage_02_maximum_flow_foundations.md
  stage_02_proof_notes.md     # Write during implementation; not supplied by this file
```

The new `max_flow.py` may import Stage 01 models and structural validation. It must not import `residual.py` or either solver. `residual.py` may import `max_flow.py`; solvers may import both. The CLI imports the solvers and existing `io.load_network`. Avoid circular imports.

### 5.2 Data contracts

These are declarations of required interfaces, not supplied implementations:

```python
# max_flow.py
from dataclasses import dataclass
from typing import Literal
from .models import FlowNetwork


@dataclass(frozen=True)
class MaxFlowProblem:
    network: FlowNetwork
    source: str
    sink: str


@dataclass(frozen=True)
class MaxFlowResult:
    algorithm: Literal["ford_fulkerson", "edmonds_karp"]
    value: int
    flow: dict[str, int]
    source_side: frozenset[str]
    sink_side: frozenset[str]
    cut_capacity: int
    augmentations: int
```

Own the returned flow dictionary; never alias a caller's candidate mapping. A frozen dataclass does not make its contained dictionary deeply immutable. Do not claim otherwise. Keep domain validation explicit, not in constructors.

```python
# residual.py
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ResidualArc:
    edge_id: str
    source: str
    target: str
    direction: Literal[1, -1]
    residual_capacity: int


ResidualGraph = dict[str, tuple[ResidualArc, ...]]
```

The logical arc identity is `(edge_id, direction)`. Two arcs with identical endpoints can still represent different legal updates.

### 5.3 Functions

```python
# max_flow.py
from collections.abc import Mapping


def validate_max_flow_problem(problem: MaxFlowProblem) -> None: ...


def validate_max_flow(
    problem: MaxFlowProblem, flow: Mapping[str, int]
) -> int: ...  # Return the feasible flow's value; not an optimality check.


def validate_max_flow_result(
    problem: MaxFlowProblem, result: MaxFlowResult
) -> None: ...  # Check feasibility, reported value, partition, and equal cut capacity.
```

The result validator independently recomputes net outflows and cut capacity from the original network. Reject an invalid algorithm name, invalid/noninteger numerical result fields, negative augmentation count, incorrect value, invalid cut partition, or unequal value/cut capacity. It checks that the count is a nonnegative integer, but does not claim to reconstruct the actual execution count from a final flow.

```python
# residual.py
from collections.abc import Mapping
from .max_flow import MaxFlowProblem


def build_residual(
    problem: MaxFlowProblem, flow: Mapping[str, int]
) -> ResidualGraph: ...


def augment_flow(
    problem: MaxFlowProblem,
    flow: Mapping[str, int],
    path: tuple[ResidualArc, ...],
) -> tuple[dict[str, int], int]: ...  # Return (new_flow, bottleneck).


def reachable_vertices(
    residual: ResidualGraph, source: str
) -> frozenset[str]: ...
```

```python
# ford_fulkerson.py
from .max_flow import MaxFlowProblem, MaxFlowResult
from .residual import ResidualArc, ResidualGraph


def find_path_dfs(
    residual: ResidualGraph, source: str, sink: str
) -> tuple[ResidualArc, ...] | None: ...


def solve_ford_fulkerson(problem: MaxFlowProblem) -> MaxFlowResult: ...
```

```python
# edmonds_karp.py
from .max_flow import MaxFlowProblem, MaxFlowResult
from .residual import ResidualArc, ResidualGraph


def find_path_bfs(
    residual: ResidualGraph, source: str, sink: str
) -> tuple[ResidualArc, ...] | None: ...


def solve_edmonds_karp(problem: MaxFlowProblem) -> MaxFlowResult: ...
```

Path-search and reachability helpers consume a residual graph produced by `build_residual`. Require the supplied terminal IDs to exist; path search rejects identical source and sink. Return `None` when no path exists, not an empty successful path. Paths contain **arcs**, not just node IDs.

Use useful `ValueError` messages for invalid domain inputs. Preserve Stage 01 file/JSON errors. Do not fabricate a successful solver result when validation fails.

## 6. Residual arcs and safe updates

### 6.1 Build a fresh snapshot

For an original edge `e: u -> v` with capacity `c` and current flow `f`:

```text
forward arc: u -> v, edge_id=e.id, direction=+1, residual_capacity=c-f
reverse arc: v -> u, edge_id=e.id, direction=-1, residual_capacity=f
```

Include only arcs with positive residual capacity in the active residual graph. Include a dictionary key for every node even if its adjacency tuple is empty. Do not store flow on the original `Edge`.

Validate the maximum-flow problem and candidate before building. Iterate original edges in their stored tuple/JSON-array order, appending each positive forward arc and then each positive reverse arc to the appropriate adjacency lists. Freeze those lists to tuples before returning. This ordering makes manual traces reproducible.

Rebuild the residual graph after each augmentation. This is a deliberately simple snapshot implementation; it is not the dynamic graph structure from Paper 1. Old arc objects are not a mutable, live view of the new state.

### 6.2 Validate a path before changing anything

`augment_flow` must:

1. Validate the problem and current candidate using the maximum-flow contract.
2. Reject an empty path, unknown original edge, or direction other than integer `+1` or `-1` (reject booleans).
3. Check each arc's endpoints against its original edge and direction.
4. Recompute each arc's current residual capacity. Reject a noninteger or boolean snapshot capacity, a nonpositive capacity, or a snapshot whose `residual_capacity` differs from the current value; do not trust stale arcs.
5. Require a continuous simple path from the problem's source to its sink, with no repeated vertices.
6. Compute `delta` as the minimum current residual capacity on the path.
7. Copy the flow dictionary and apply `new_flow[arc.edge_id] += arc.direction * delta` for each arc.
8. Verify the new state is feasible and its value equals the old value plus `delta`.
9. Return the new mapping and `delta` without modifying the input objects.

Even a failed update must leave its inputs unchanged. Check all path conditions before applying updates to the returned copy.

For valid current arcs, a reverse step means **decreasing the selected original edge's flow**. It does not add a new physical edge, require negative original flow, or cancel a different edge with the same endpoints.

## 7. Algorithms and proof obligations

### 7.1 Shared method

Each solver validates its input, initializes every original edge to zero, and repeats:

```text
build current residual snapshot
find an s-to-t path using this solver's search rule
if no path exists: stop
augment by the bottleneck
increment the successful-augmentation counter
```

After stopping, compute residual reachability, form the cut, calculate its original-edge capacity, construct the result, and validate the result before returning it. Count successful updates only, not the final unsuccessful search.

Small pure helpers may be shared. Do not implement one solver by calling the other; their search functions must independently implement DFS and BFS. A common residual implementation is expected.

### 7.2 DFS selection for Ford-Fulkerson

Ford-Fulkerson in the lecture permits any augmenting path. Our selected implementation uses DFS with stored adjacency order.

Use an iterative DFS that behaves like recursive depth-first traversal: descend through the first unvisited neighbor immediately, remember where to resume that vertex's adjacency scan, and backtrack when exhausted. This avoids Python recursion-depth failures and makes the rerouting fixture follow the specified first path.

Reset visited and parent information for each search. Record the actual parent **arc**. Do not mark all neighbors at once and then assume the resulting traversal matches recursive-order DFS.

### 7.3 BFS selection for Edmonds-Karp

Use `collections.deque`, mark nodes when enqueued, and record parent arcs. Explore in stored adjacency order. BFS selects the fewest-edge path; it does not select a cheapest or largest-bottleneck path. This follows PDF page 150.

### 7.4 Proof notes to write

In `docs/stage_02_proof_notes.md`, give short source-linked arguments for:

- **Initialization:** zero flow is feasible under this stage's zero-lower-bound contract.
- **Preservation:** forward updates respect upper bounds, reverse updates keep original flow nonnegative, and each internal path vertex has zero change in net outflow.
- **Progress:** augmentation increases source net outflow by the positive bottleneck.
- **Termination:** integer capacities keep updates integral; value increases by at least one and is bounded by total capacity leaving the source.
- **Optimality:** with no residual path, the reachable-set cut has saturated outgoing original edges and zero incoming original flow. Flow value equals its capacity, an upper bound for every feasible flow.
- **Edmonds-Karp bound:** summarize nondecreasing BFS distances and the critical-arc argument from PDF pages 151-155. Do not substitute timing tests for this argument.

Use the lecture's net-balance invariant carefully: actual incoming or outgoing original flow may decrease when reverse arcs are used. What must stay unchanged at an intermediate node is `outflow - inflow`.

### 7.5 Complexity: distinguish the lecture from this implementation

The lecture gives Ford-Fulkerson `O(m*C)` for integer capacities and Edmonds-Karp `O(n*m^2)`, with `C` the total capacity leaving the source. Here `n` counts original nodes and `m` counts original edges, not residual arcs. These are operation-count bounds, not claims of constant-time arithmetic for arbitrarily large integers.

**Implementation accounting, derived for this design:** rebuilding and validating full snapshots costs `O(n+m)` per iteration. With `A` successful augmentations, allow `O((A+1)*(n+m))` total work and `O(n+m)` working memory; this includes final checks and isolated nodes. Integer capacities give `A <= F_max <= C`. The lecture's Edmonds-Karp critical-arc argument gives `A = O(n*m)`; applying it to this design gives the conservative bound `O((n*m+1)*(n+m))`.

When `n = O(m)`, as for the lecture's nontrivial all-vertices-on-path setting, these recover the familiar `O(m*(C+1))` and `O(n*m^2)` forms. Do not claim the simplified implementation has a smaller bound without accounting for its actual validation and reconstruction work. Stage 07, not this stage, owns performance experiments.

## 8. Fixtures and expected results

Use Stage 01's unchanged network JSON schema: exactly `nodes` and `edges`. All nodes have balance `0`; all edges have unit cost `0` and lower capacity `0`. Source and sink are supplied separately to the API/CLI.

### 8.1 Required reverse-edge example

Save the following as `examples/stage2/rerouting.json`. Topology and unit capacities come from Lecture 7 PDF pages 129-132; IDs and array order are repository choices.

```json
{
  "nodes": [
    {"id": "s", "balance": 0},
    {"id": "a", "balance": 0},
    {"id": "b", "balance": 0},
    {"id": "t", "balance": 0}
  ],
  "edges": [
    {"id": "sa", "source": "s", "target": "a", "capacity": 1, "unit_cost": 0},
    {"id": "ab", "source": "a", "target": "b", "capacity": 1, "unit_cost": 0},
    {"id": "bt", "source": "b", "target": "t", "capacity": 1, "unit_cost": 0},
    {"id": "sb", "source": "s", "target": "b", "capacity": 1, "unit_cost": 0},
    {"id": "at", "source": "a", "target": "t", "capacity": 1, "unit_cost": 0}
  ]
}
```

```text
Original network; all capacities are 1:

s -----> a -----> t
|        |
|        v
+------> b -----> t

Both occurrences of t in this drawing denote the same node.
```

Manual trace under the specified DFS ordering:

| Step | Selected residual arcs | Delta | Flow value | Original ab flow |
|---|---|---:|---:|---:|
| Initial | None | - | 0 | 0 |
| First update | sa forward, ab forward, bt forward | 1 | 1 | 1 |
| Second update | sb forward, ab reverse, at forward | 1 | 2 | 0 |

Final original-edge mapping:

```json
{"sa": 1, "ab": 0, "bt": 1, "sb": 1, "at": 1}
```

Expected certificate: value `2`, source side `{s}`, sink side `{a,b,t}`, cut capacity `2`. DFS performs two augmentations. BFS also performs two, but selects `s-a-t` and `s-b-t` and need not use a reverse arc. Therefore the reverse-step test must inspect DFS or explicitly call the residual/update helpers, not require BFS to follow DFS's route.

### 8.2 Additional fixtures

The rows below completely specify the remaining network fixtures. List nodes in the given order. List edges in the displayed order; notation is `ID: source -> target (capacity)`. Add the required zero balance and cost fields to produce JSON. These are our own test cases except `lecture_23.json`.

| File | Nodes | Edges in order | Expected maximum |
|---|---|---|---:|
| `bottleneck.json` | s, a, t | sa: s->a (5); at: a->t (3) | 3 |
| `parallel_edges.json` | s, t | line_a: s->t (5); line_b: s->t (5) | 10 |
| `opposite_edges.json` | s, a, b, t | sa: s->a (3); ab: a->b (3); ba: b->a (2); bt: b->t (3) | 3 |
| `disconnected.json` | s, a, t | sa: s->a (2) | 0 |
| `lecture_23.json` | s, v1, v2, v3, v4, t | sv1: s->v1 (16); sv2: s->v2 (13); v2v1: v2->v1 (4); v1v3: v1->v3 (12); v3v2: v3->v2 (9); v2v4: v2->v4 (14); v4v3: v4->v3 (7); v3t: v3->t (20); v4t: v4->t (4) | 23 |

For the bottleneck fixture, the final reachable source side is `{s,a}`, giving cut capacity 3. For disconnected, it is `{s,a}`, giving cut capacity 0 and no successful augmentation. For the parallel fixture, both original edges carry 5.

For the opposite-edge fixture, use the manually supplied feasible candidate below to test residual identity separately from zero-start solver execution:

```json
{"sa": 1, "ab": 2, "ba": 1, "bt": 1}
```

Its value is 1. The residual graph contains two distinct arcs from `a` to `b`: forward `ab` with residual 1, and reverse `ba` with residual 1. It also contains reverse `ab` with residual 2 and forward `ba` with residual 1 from `b` to `a`. Do not merge or overwrite these arcs.

The lecture's 23-unit example has this feasible certificate (PDF pages 159 and 166):

```text
flow = {sv1:12, sv2:11, v2v1:0, v1v3:12, v3v2:0,
        v2v4:11, v4v3:7, v3t:19, v4t:4}
source_side = {s, v1, v2, v4}
sink_side = {v3, t}
cut_capacity = 12 + 7 + 4 = 23
```

BFS with the specified ordering gives deltas `12, 4, 7`. Both solvers must return value 23 and valid certificates. A different feasible maximum-flow vector is not incorrect solely because it differs from this example; compare feasibility and certified value, not a unique-flow assumption.

## 9. CLI and JSON behavior

Reuse `load_network` without adding new JSON fields or changing Stage 01. The CLI constructs `MaxFlowProblem(network, source, sink)` and dispatches to the selected solver.

```bash
python -m renewable_routing.stage2 examples/stage2/rerouting.json --source s --sink t --algorithm ford-fulkerson
python -m renewable_routing.stage2 examples/stage2/rerouting.json --source s --sink t --algorithm edmonds-karp
```

Require `--source`, `--sink`, and `--algorithm`; the only algorithm values are `ford-fulkerson` and `edmonds-karp`. There is one positional argument, the network file. No candidate-flow file is required because the solver finds the flow.

Expected successful output for the first command:

```text
Algorithm: ford-fulkerson
Maximum flow: 2
Cut capacity: 2
Certificate: verified
Augmentations: 2
Flow by edge: {"ab": 0, "at": 1, "bt": 1, "sa": 1, "sb": 1}
Source side: ["s"]
Sink side: ["a", "b", "t"]
Cost optimization: not performed
```

Use sorted JSON object keys and sorted partition arrays for deterministic display. The internal algorithm uses input adjacency order, not display order. State `Certificate: verified` only after actually running the result validator.

Exit `0` for a verified result, including value zero. Use `1` and an `ERROR:` message on stderr for expected input/file/domain failures; no traceback or success result for those failures. Use `argparse`'s normal code `2` for missing/invalid arguments. Do not hide unexpected programming errors.

## 10. Required tests

Preserve and rerun all Stage 01 tests. Test groups below may be parametrized; their count is not a required number of collected test functions.

| ID | Requirement | Expected result |
|---|---|---|
| S2T01 | Supported zero-cost/zero-balance problem | Accepted; zero candidate has value 0. |
| S2T02 | Missing, malformed, or identical terminals | Useful validation error. |
| S2T03 | Nonzero balances, positive lower bounds, nonzero costs | Rejected without mutating or normalizing input. |
| S2T04 | Original edge into s or out of t; self-loop | Rejected under this stage's contract. |
| S2T05 | Float, bool, numeric string, negative flow, missing/extra flow ID | Rejected; no implicit zeros or coercion. |
| S2T06 | Capacity-compliant but unbalanced intermediate node | Rejected by maximum-flow state validator. |
| S2T07 | Single edge of capacity 5 with flow 3 | Residual forward 2, reverse 3, retaining the original ID. |
| S2T08 | Empty/zero-capacity adjacency and isolated node | Present node keys; no positive arcs for zero capacity. |
| S2T09 | Rerouting trace with DFS helpers | First path sa-ab-bt; second uses reverse ab; final ab=0 and value=2. |
| S2T10 | Rerouting trace with BFS helpers | First path sa-at, second sb-bt; value=2. |
| S2T11 | Bad update path: empty, disconnected, wrong terminals, repeated vertex, unknown edge, invalid direction, stale or nonpositive residual | Error before any input mutation. |
| S2T12 | Bottleneck fixture | Delta 3; final flow 3 on each edge; cut capacity 3. |
| S2T13 | Parallel fixture | Both edge IDs preserved; maximum and cut capacity 10. |
| S2T14 | Opposite-edge candidate from Section 8.2 | Four distinct ab/ba residual arcs, with the stated identities and capacities. |
| S2T15 | Augment opposite-edge candidate using reverse ba | Cancel ba, do not change ab; remain feasible with value increased by 1. |
| S2T16 | Disconnected sink and two-node empty-edge graph | Successful result value 0, valid zero-capacity cut, zero augmentations. |
| S2T17 | Both solvers on every fixture | Expected maximum value; capacity, conservation, and certificate checks pass. |
| S2T18 | Six-node lecture fixture with BFS | Value 23; three successful augmentations; deltas 12,4,7 observable through helpers. |
| S2T19 | Tampered result: wrong value, flow, partition, or cut capacity | Result validator rejects it. |
| S2T20 | Certificate with invalid algorithm/count types or negative count | Rejected; booleans are not integers for this purpose. |
| S2T21 | Repeated solve and reordered candidate mapping | Stable result for the same input order; no shared state or input mutation. |
| S2T22 | Different edge order | Still a feasible optimal value; paths and flow vectors may change. |
| S2T23 | Small independently enumerated cuts | Both solver values equal the independent minimum cut. |
| S2T24 | CLI success, zero-flow case, bad arguments, unsupported input, malformed JSON/missing file | Required outputs and codes; no minimum-cost claim. |
| S2T25 | Stage 01 regression suite | All prior behavior, schemas, and costs 9, 15, 20 preserved. |
| S2T26 | Iterative search on a long chain | No reliance on raising the Python recursion limit; DFS and BFS find the path. |

For S2T15, on the given candidate use the path `sa forward -> ba reverse -> bt forward`, each with positive residual capacity. Delta is 1; the new candidate is `{sa:2, ab:2, ba:0, bt:2}`. The original `ab` flow stays 2.

For S2T23, create a deterministic test-only minimum-cut oracle: enumerate sets containing `s` and excluding `t`, independently sum original outgoing capacities, and take the minimum. Limit this to 2-6 nodes and a small fixed batch, for example 20 cases using `random.Random(0)` and capacities 0-6. Include parallel edges and internal opposite directions while respecting terminal restrictions. No production solver may enumerate cuts or use this oracle.

Do not rely only on the two solvers agreeing: they share residual code and could share a defect. Hand traces and the independently calculated cut oracle supply different checks. The oracle is a test design derived from the cut definition, not a solver implementation copied from the lecture.

## 11. Implementation order and acceptance

### Work sequence

1. Inspect Stage 01 and run its baseline tests. Add the maximum-flow contract and its tests.
2. Implement immutable residual snapshots and pure augmentation; pass the manual cancellation tests before building complete solvers.
3. Implement iterative DFS selection and Ford-Fulkerson; verify the unit rerouting fixture.
4. Implement BFS selection and Edmonds-Karp; verify both lecture examples.
5. Return and independently validate cut certificates; add tampering and exhaustive-cut tests.
6. Add the CLI and all JSON fixtures; run the full regression suite and CLI checks.
7. Write the short proof notes and update only relevant README/roadmap status and document links. Mark implementation complete only with actual evidence.

Do not reinitialize the package, alter Stage 01 signatures, or add third-party runtime dependencies. Necessary private-helper refactoring must preserve all existing behavior and be justified by passing regression tests.

### Commands after implementation

Run in the existing project environment. Use installation commands from Stage 01 only if needed and authorized.

```bash
python --version
python -m pytest -q
python -m renewable_routing.stage1 examples/stage1/two_link_network.json examples/stage1/flow_optimal.json
python -m renewable_routing.stage2 examples/stage2/rerouting.json --source s --sink t --algorithm ford-fulkerson
python -m renewable_routing.stage2 examples/stage2/rerouting.json --source s --sink t --algorithm edmonds-karp
python -m renewable_routing.stage2 examples/stage2/lecture_23.json --source s --sink t --algorithm edmonds-karp
python -m renewable_routing.stage2 examples/stage2/disconnected.json --source s --sink t --algorithm edmonds-karp
```

Also verify expected failure cases and their exit codes. Record the Python version actually used; execution on another version does not verify Python 3.10 execution.

### Definition of done

- [ ] The Stage 01 baseline and regression suite pass without relaxed requirements.
- [ ] Maximum-flow validation is separate from fixed-balance candidate validation.
- [ ] Unsupported balances, costs, and lower bounds fail explicitly.
- [ ] Original edge identity survives parallel and opposite-direction residual updates.
- [ ] Both solvers start at zero and return valid maximum-flow/cut certificates.
- [ ] The unit rerouting test actually cancels ab from 1 to 0.
- [ ] The 23-unit lecture example agrees with its known certificate.
- [ ] Disconnected and zero-capacity cases return a certified zero flow where appropriate.
- [ ] S2T01-S2T26 are mapped to actual tests and executed evidence.
- [ ] CLI behavior, malformed inputs, and exit codes are verified.
- [ ] Proof notes cite the lecture and distinguish implementation choices from source statements.
- [ ] Documentation reports actual results and does not count these as minimum-cost solvers.
- [ ] No Stage 03, GIS, learning, benchmark, or outage implementation has been added.

Report according to Stage 00: changed files, requirement-to-test mapping, actual commands/results, environment, unresolved issues, and `Next stage: not started`. No code or tests have been executed in the user's repository merely by supplying this specification.

Minimal Cursor request after reviewing this contract:

```text
Implement Stage 02 according to docs/stage_02_maximum_flow_foundations.md.
```

## 12. Short lecturer questions and answers

**1. What changes from Stage 01 to Stage 02?**  
Stage 01 checks a supplied fixed-balance flow. Stage 02 finds maximum source-to-sink throughput under its separate contract.

**2. Why do residual arcs need an original edge ID and a direction?**  
Endpoints alone cannot distinguish parallel edges or a forward original edge from cancellation of an opposite original edge.

**3. How do Ford-Fulkerson and Edmonds-Karp differ here?**  
Our Ford-Fulkerson uses DFS; Edmonds-Karp uses BFS to select a fewest-edge augmenting path. Both use bottleneck updates.

**4. What certifies that the returned flow is maximum?**  
A feasible flow and a valid source/sink cut with equal value and capacity. No feasible flow can exceed that cut.

**5. Does finishing Stage 02 satisfy the two minimum-cost-flow methods requirement?**  
No. These methods maximize throughput without optimizing cost; the classical minimum-cost methods are later stages.
