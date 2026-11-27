# Project Recall Prompt

> Save at `docs/PROJECT_RECALL_PROMPT.md`. Paste the prompt below into a new conversation or agent task, and provide the referenced files when available. Update the final request block before use. This is a context handoff, not persistent memory or proof that code exists.

```text
You are continuing my MCS Advanced Algorithms Project 6:
"Renewable-Energy Routing: Almost-Linear Flow Theory Meets GIS Data."

PROJECT GOAL
Build a regional network-flow model that meets electricity demand at minimum
cost while respecting generation and transmission limits. Combine flow
algorithms, GIS-based candidate-link selection, geospatial representation
learning, and rerouting after generation-site outages. This is a network-flow
abstraction, not a validated electrical power-flow simulator.

ASSIGNMENT REQUIREMENTS
Part A: Study Paper 1; write an outline of its reduction from minimum-cost
flow to repeated minimum-ratio-cycle computations; implement at least two
classical minimum-cost-flow methods and a simplified minimum-ratio-cycle-driven
cycle-canceling method that reaches optimal flows on supported small graphs.
Check correctness against a reference solver and compare runtime versus m,
the number of original graph edges.

Part B: Build a regional GIS microgrid model; implement PostGIS-backed spatial
range queries and a grid or geohash baseline; measure query cost versus link
radius; choose one representation technique from Paper 2 to estimate demand
or generation capacity per cell; compare with a trivial baseline and evaluate
routing impact; demonstrate rerouting after simulated generation outages.

Grading as provided: Engine Checkpoint 10%; Codebase, Test Suite, and Technical
Paper 15%; Live Project Defense 5%; total project weight 30%.

WORKING PREFERENCES
- Use a top-down approach: assignment target -> deliverable -> required
  concepts -> exact lecture/paper locations -> proof/test obligations.
- Do not reteach lectures from the beginning or implement unrelated topics.
- Direct teaching/discussion: Vietnamese and English.
- Code, repository docs, GitHub material, prompts, and implementation reports:
  English only.
- End each completed stage explanation with at most five short likely lecturer
  questions and answers. Repository versions are English only.
- Work one stage at a time. A roadmap or recall request does not authorize code.

READ AVAILABLE PROJECT FILES FIRST
- README.md
- AGENTS.md
- docs/stage_00_repository_foundation.md
- docs/PROJECT_ROADMAP.md
- The active stage specification; Stage 01 is
  docs/stage_01_problem_definition.md

Read current files rather than assuming this summary is still current.
Stage 00 defines how to work; the active specification defines what to build.
Keep this recall prompt subordinate to those contracts and the user's approved
changes. Identify material conflicts rather than silently reconciling them.

STAGE ROADMAP
00 Repository foundation, conventions, workflows, and guardrails.
01 Problem definition, candidate validation, and cost evaluation; no solver.
02 Residual networks, Ford-Fulkerson, Edmonds-Karp, and max-flow/min-cut tests.
03 First classical minimum-cost-flow solver; proposed method: successive
   shortest paths. Begin independent reference checking here.
04 Second distinct classical minimum-cost-flow solver; method undecided
   (for example, cost scaling or network simplex).
05 Simplified minimum-ratio-cycle-driven cycle canceling on small graphs.
06 Paper 1 reduction proof outline and the 10% engine checkpoint.
07 Reproducible solver benchmarks versus original edge count m.
08 GIS data, units, provenance, and regional microgrid network construction.
09 PostGIS spatial indexing and grid/geohash comparison versus link radius.
10 One geospatial representation method, demand/capacity estimation, baseline
   comparison, and routing-impact evaluation.
11 Integrated routing, generation-outage rerouting, and explicit shortfall
   handling when full demand cannot be served.
12 Technical paper, reproducibility, and live-defense preparation.

Stages 00-02 preserve the established sequence. Stages 03-12 are a proposed
work breakdown, not finalized implementation specifications. Do not implement
from this outline alone. Define/review missing contracts first.

KNOWN STATUS AT THIS HANDOFF
README.md, AGENTS.md, and the Stage 00-02 specifications are present. Stage 01
candidate validation/evaluation and Stage 02 maximum-flow foundations are
implemented. The latest Stage 02 handoff verified 74 tests on Python 3.10.22,
the documented Stage 1 and Stage 2 commands, the Stage 2 demonstration, and an
expected CLI domain failure. No commit, benchmark, or later-stage experiment is
claimed. Reinspect current code and evidence when resuming.

EXISTING IMPLEMENTATION CONTRACT
Target Python 3.10; package src/renewable_routing/. Stage 01 and Stage 02
runtime code use only the standard library; tests use pytest. Later
dependencies require an approved stage-specific reason.

Stage 01: frozen Node, Edge, FlowNetwork; FlowEvaluation; validate_network,
validate_flow, evaluate_flow, load_network, and load_flow. Follow the exact
signatures, schemas, CLI behavior, and T01-T22 requirements in its specification.

outflow - inflow = Node.balance
positive balance = required supply; negative = required consumption
sum(balances) = 0
0 <= lower_capacity <= edge flow <= capacity
cost = sum(unit_cost * edge flow)

Node.balance is prescribed injection, not available generation capacity.
Use integer numerical values, rejecting booleans and silent coercion; signed
costs are allowed. Keep candidate flows separate, keyed by unique edge IDs.
Preserve parallel and opposite-direction original edges independently.
Do not mutate caller inputs or silently repair data.

Fixture checks: flows (5,1) cost 9; (3,3) cost 15; (6,0) fails capacity;
(5,0) fails balance; transit fixture costs 20. Stage 01 never searches for a
flow or claims optimality. One invalid candidate does not prove infeasibility.

Stage 02 uses MaxFlowProblem and MaxFlowResult under a separate zero-balance,
zero-lower-bound, zero-cost contract. ResidualArc retains original edge ID and
direction. Ford-Fulkerson uses deterministic iterative DFS; Edmonds-Karp uses
BFS. Both return validated equal-capacity cut certificates. Do not force
maximum-flow source/sink amounts to meet Stage 01 fixed balances, and do not
claim that these algorithms optimize cost.

PERMANENT GUARDRAILS
Use the Stage 00 workflows: inspect-stage, implement-stage, verify-contract,
design-tests, debug-regression, review-handoff. They are documented recipes,
not evidence of installed editor skills/plugins.
Preserve unrelated work and contracts. Do not weaken tests, fabricate results,
expose secrets, add unapproved dependencies, make unauthorized downloads,
perform destructive actions, commit, or push without authorization.
Report actual verification commands, results, environment, and remaining gaps.

Ford-Fulkerson and Edmonds-Karp are maximum-flow foundations: they do not count
as the two required classical minimum-cost-flow methods. A reference-solver
wrapper is not an independent student implementation. The simplified cycle
method does not inherit Paper 1's almost-linear runtime guarantee. The proof
of the toy method is not a substitute for the paper-specific reduction outline.
Lower routing cost alone does not demonstrate better predictions when demand
amounts differ. Do not silently lower demand after an outage.

SUPPLIED STUDY MATERIALS
- Uploaded_Lecture06_computational_geometry.pdf
- Uploaded_Lecture07_graph_theory_advanced.pdf
- [2025] Maximum Flow and Minimum-Cost Flow in Almost-Linear Time.pdf
- [2025] Representation learning for geospatial data.pdf

Stage 01 reading pointers: Lecture 7 PDF pages 123-124; Paper 1 PDF pages 2-3.
Stage 02 reading pointers: Lecture 7 PDF pages 128-142 and 150-155.
Use PDF viewer pages, distinguish printed slide numbers, and reopen actual
sources before explaining source-specific content. Do not fetch the papers
online. If a source is inaccessible, say so and do not invent its contents.

CURRENT REQUEST - FILL IN BEFORE USE
Mode: [discuss / define / implement / review]
Active stage: [NN or planning only]
Target: [the requested outcome]
Specification path: [path, or "not yet written"]
Last verified implementation/test evidence: [actual evidence, or "unknown"]
Open decisions/blockers: [details, or "none reported"]

Start with the requested task. Keep global rules predefined; do not ask me to
repeat them. For implementation, inspect the repository and approved contract
first. For a missing contract, define it when requested rather than inventing
an implementation. Stop at the requested scope boundary.
```
