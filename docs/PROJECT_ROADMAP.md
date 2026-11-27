# Project 6: Roadmap and Document Index

> **Project:** Renewable-Energy Routing: Almost-Linear Flow Theory Meets GIS Data  
> **Course:** Advanced Algorithms, Master of Computer Science (MCS)  
> **Repository target:** `docs/PROJECT_ROADMAP.md`  
> **Implementation target:** Python 3.10; package `renewable_routing`  
> **Status:** Planning and recall document, not evidence of completed implementation.

Stages 00-02 preserve the sequence already established in our discussions and documents. Stages 03-12 below are a **proposed decomposition of the remaining assignment**, created in response to the request for a complete roadmap. They are not the lecturer's stage numbering and are not finalized implementation contracts.

This roadmap does not override Stage 00, change existing APIs, or authorize implementation of all stages. Write and review each missing stage specification before implementing it. Do not create placeholder modules or all future stage files merely because they are listed here.

## Contents

- [1. Project summary](#1-project-summary)
- [2. Assignment deliverables and grading](#2-assignment-deliverables-and-grading)
- [3. Current status and evidence](#3-current-status-and-evidence)
- [4. Stage list and success targets](#4-stage-list-and-success-targets)
- [5. Dependencies and checkpoints](#5-dependencies-and-checkpoints)
- [6. Document index and stage table of contents](#6-document-index-and-stage-table-of-contents)
- [7. Working method and language rules](#7-working-method-and-language-rules)
- [8. Existing contracts to preserve](#8-existing-contracts-to-preserve)
- [9. Decisions still open](#9-decisions-still-open)
- [10. Continuation and progress handoff](#10-continuation-and-progress-handoff)
- [11. Sources and provenance](#11-sources-and-provenance)

## 1. Project summary

Build a regional microgrid routing model that satisfies electricity demand at minimum total cost while respecting generation and transmission limits. Connect three components: flow optimization, geographic link selection, and learned demand or generation estimates.

The project has two parts, as specified in the assignment supplied in the conversation:

**Part A - Theory and small-scale replication.** Study Paper 1, outline its reduction from minimum-cost flow to repeated minimum-ratio-cycle computations, implement at least two classical minimum-cost-flow methods, and implement a simplified minimum-ratio-cycle-driven cycle-canceling method on small graphs.

**Part B - Engineering.** Build a network from regional GIS layers, use indexed spatial range queries to select candidate links, estimate demand or generation capacity using one representation-learning technique from Paper 2, compare against a trivial baseline, optimize routing, and demonstrate rerouting after a generation outage.

The final system should report a routing and its cost when feasible. If a scenario cannot meet all demand, report that fact; partial service requires an explicit model rather than silently reducing the requested demand.

This is a network-flow abstraction, not a validated electrical power-flow simulator. The simplified cycle implementation is not the full almost-linear-time algorithm and must not claim its runtime guarantee.

## 2. Assignment deliverables and grading

The weights below reproduce the assignment pasted by the user. The stage mapping is our proposed work organization, not additional grading criteria.

| Deliverable | Weight as assigned | Required evidence | Roadmap mapping |
|---|---:|---|---|
| Engine Checkpoint | 10% | Classical and cycle-based minimum-cost-flow solvers; correctness tests against a reference solver; written outline of Paper 1's reduction. | Stages 03-06, supported by 00-02. |
| Codebase, Test Suite, and Technical Paper | 15% | Microgrid optimizer; PostGIS-backed queries; chosen representation-based demand/capacity model; experiments; report connecting measured scaling to theory. | Stages 07-12 plus the tested engine from 03-06. |
| Live Project Defense | 5% | Real-time rerouting after a simulated generation-site outage. | Stage 11 demonstration, prepared for defense in Stage 12. |
| **Total** | **30%** | All three deliverables. | Complete project. |

Three experimental comparisons must remain visible in the plan:

1. Flow-solver running time versus original edge count `m` on generated networks.
2. Indexed spatial-query cost versus link-selection radius, compared with a grid or geohash baseline.
3. Learned demand/capacity estimates versus a trivial baseline, and their effect on routing cost and service outcomes.

A library reference solver is useful for checking correctness. A wrapper around that library is not, by itself, an independent student implementation. Keep this distinction explicit when documenting the two classical methods.

## 3. Current status and evidence

This snapshot describes what has been supplied or discussed in this conversation. It is not a live inspection of the user's Git repository.

| Item | Known status |
|---|---|
| `README.md` | Supplied. Describes the overview and incremental roadmap. |
| `AGENTS.md` | Supplied. Short entrypoint to policy and the requested stage. |
| Stage 00 specification | Supplied: `docs/stage_00_repository_foundation.md`. |
| Stage 01 specification | Supplied: `docs/stage_01_problem_definition.md`. |
| Stage 01 discussion | Covered problem definition; five short defense questions were supplied. |
| Stage 02 discussion | Covered residual networks, reverse edges, augmentation, Ford-Fulkerson, Edmonds-Karp, and the relevant proof/lecture locations. |
| Stage 02 implementation specification | Supplied at `docs/stage_02_maximum_flow_foundations.md`; implementation and proof notes are present. |
| Stages 03-12 | Proposed roadmap only. Detailed specifications remain to be written. |
| Standard Stage Execution addition to `AGENTS.md` | Proposed in discussion. Whether it has been merged into the user's repository is unverified. |
| Code and test execution | Stages 01-02 have implementation and test evidence; use the latest implementation handoff for exact commands and results. No benchmark evidence is claimed. |

Before resuming work, inspect current files and evidence. A source file being present is different from its behavior being tested.

## 4. Stage list and success targets

These rows define high-level targets. API choices, solver assumptions, fixture values, dependencies, and exact acceptance tests for future stages belong in their individual specifications.

| Stage | Title | Target and scope | Evidence needed to close the stage |
|---|---|---|---|
| **00** | Repository foundation | Apply shared structure, conventions, agent instructions, workflows, and guardrails. Bootstrap documentation links and `.gitignore` only. | Correct policy/agent files, working relative links, reviewed changes, and no application implementation added under Stage 00. |
| **01** | Problem definition and validation | Represent a fixed-balance flow network, validate a caller-supplied candidate, and calculate its cost. Add the specified JSON fixtures, CLI, and tests. | T01-T22 requirements covered; expected costs 9, 15, and 20; invalid candidates rejected; no solver or optimality claim. |
| **02** | Maximum-flow foundations | Implement residual arcs, flow updates, Ford-Fulkerson, and Edmonds-Karp under a separate, explicit maximum-flow contract. | Rerouting example, capacity/conservation tests, and maximum-flow/minimum-cut agreement. Does not count as either required minimum-cost solver. |
| **03** | First classical minimum-cost-flow solver | Proposed first method: successive shortest paths. Define the supported problem, initialization, cost handling, and result contract before implementation. Begin reference-solver checking here. | Student implementation with feasible, minimum-cost results on the approved small cases; independent reference agreement; supported and rejected cases documented. |
| **04** | Second classical minimum-cost-flow solver | Select a different classical method, such as cost scaling or network simplex, and implement it under a compatible result contract. Method choice remains open. | A genuinely distinct second implementation, shared correctness tests, and agreement with an independent reference on supported instances. |
| **05** | Simplified minimum-ratio-cycle method | Define the simplified ratio, allowed residual cycles, initial feasible flow, update amount, stopping rule, and small-graph scope. Implement cycle-based cost improvement. | Traceable cost-reducing updates, feasibility preservation, a correctness/termination argument for the stated variant, and reference-checked optimal small-graph results. |
| **06** | Paper 1 proof outline and engine checkpoint | Explain the paper's reduction to repeated approximate minimum-ratio-cycle problems and distinguish it from Stage 05. Assemble the engine checkpoint evidence. | Paper-specific proof outline with source locations; two classical methods plus the simplified cycle method; correctness results against a reference. Targets the 10% checkpoint. |
| **07** | Solver benchmarking and scaling | Generate controlled network families and compare all required minimum-cost-flow methods as original edge count `m` increases. | Reproducible measurements, graph parameters, seeds, repetitions, environment, timeouts, and plots; empirical conclusions separated from theoretical guarantees. |
| **08** | GIS data and microgrid model | Define a region, geographic units, generation sites, demand hubs, available generation, transmission assumptions, units, and data provenance. Build the data-to-network adapter. | A documented regional dataset/model and tested conversion into the flow engine. Generation capacity is distinct from required net supply. |
| **09** | Spatial indexing and link selection | Implement PostGIS-backed spatial range queries and a grid or geohash baseline. Select nearby candidate links using an explicit distance/radius rule. | Matching query results under the same distance/boundary convention; evidence of actual index use; query-cost measurements versus radius and resulting link counts. |
| **10** | Geospatial representation and estimation | Choose one technique from Paper 2 to estimate demand or generation capacity per cell. Compare it with a simple baseline, such as population-proportional demand. | Documented labels and features, held-out prediction evaluation, baseline comparison, and a routing-impact experiment that reports cost alongside demand served and demand totals. |
| **11** | Integrated optimizer and outage rerouting | Connect GIS, indexed links, estimates, and a selected established minimum-cost solver. Simulate unavailable generation and rerun routing. | Reproducible before/after scenarios, valid routing, costs, rerouting time, and honest reporting of infeasibility or explicitly modeled unmet demand. |
| **12** | Technical paper, reproducibility, and defense | Assemble the report, code/test instructions, source attribution, experiment records, and live demonstration. | Reproducible code and test suite, technical paper addressing all assignment comparisons, limitations, and a rehearsed outage defense. |

### Notes on the proposed sequence

- Stage 03's successive-shortest-path choice is a proposed starting point, not a choice already implemented or mandated by the lecturer.
- Choose and specify the Stage 04 method before coding; do not count two variants of the same algorithm as two distinct methods without explicit justification and approval.
- Tests start with each implementation. Stage 06 consolidates evidence; it is not the first time correctness is checked.
- The argument for the simplified method in Stage 05 and the paper's reduction in Stage 06 are separate obligations. One does not substitute for the other.
- Solver feature support must be explicit. Stage 01's support for signed costs and positive lower bounds in validation does not establish that a particular later solver handles them.
- Begin proof notes, benchmark design, and the data/label availability review early. Do not postpone every research or data-risk decision until its numbered stage.

## 5. Dependencies and checkpoints

Suggested default execution order:

```text
Foundation:         00 -> 01 -> 02
Algorithm engine:   03 -> 04 -> 05 -> 06  [Engine Checkpoint: 10%]
Experiments:        07
Geographic model:   08 -> 09
Learning:           10
Integrated system:  11
Submission:         12                  [Code/report: 15%; defense: 5%]
```

This is a learning and delivery sequence, not a claim that every stage depends technically on every preceding one. The engine work and data-source investigation can be planned in parallel, but implementation still requires an explicit active-stage task.

**Gate A - Foundation:** Shared data and validation contracts are tested before solvers rely on them.

**Gate B - Engine:** Both classical minimum-cost methods, the simplified cycle method, independent correctness evidence, and the paper-specific proof outline are ready before calling the engine checkpoint complete.

**Gate C - System:** The regional model, indexed query path, baseline/learned estimates, and routing pipeline run together. Routing-impact results from Stage 10 can be finalized during Stage 11 integration.

**Gate D - Submission:** The required experiments and their provenance are in the report, and an outage scenario is reproducible for the live defense.

No performance target, region, dataset, machine-learning architecture, or benchmark size is fixed by this roadmap alone.

## 6. Document index and stage table of contents

### Current document index

These links assume this file is saved in `docs/` and the previously supplied files are placed at their intended repository paths.

| Document | Responsibility |
|---|---|
| [README.md](../README.md) | Project overview, status, setup, and roadmap entrypoint. |
| [AGENTS.md](../AGENTS.md) | Short instructions for agents to load policy and the active stage. |
| [Stage 00](stage_00_repository_foundation.md) | Shared conventions, architecture boundaries, reusable workflows, and guardrails. |
| [Stage 01](stage_01_problem_definition.md) | Detailed first implementation contract. |
| [Stage 02](stage_02_maximum_flow_foundations.md) | Maximum-flow contract, residual updates, solvers, fixtures, CLI, and acceptance tests. |
| [Stage 02 proof notes](stage_02_proof_notes.md) | Feasibility, progress, termination, cut optimality, and Edmonds-Karp arguments. |
| [Project roadmap](PROJECT_ROADMAP.md) | Stage list, summaries, deliverable mapping, and document index. |
| [Project recall prompt](PROJECT_RECALL_PROMPT.md) | Context handoff to paste into a new conversation or agent task. |

### Planned stage-document table of contents

The following lists implemented Stage 00-02 documents and proposed names for
later stages. Stage 03 onward still requires a reviewed specification.

```text
docs/
  stage_00_repository_foundation.md         [existing specification]
  stage_01_problem_definition.md            [existing specification]
  stage_02_maximum_flow_foundations.md       [implemented specification]
  stage_02_proof_notes.md                    [implemented proof notes]
  stage_03_successive_shortest_paths.md      [proposed]
  stage_04_second_classical_min_cost_flow.md [proposed; method undecided]
  stage_05_minimum_ratio_cycle_canceling.md  [proposed]
  stage_06_paper1_proof_and_checkpoint.md    [proposed]
  stage_07_solver_benchmarks.md              [proposed]
  stage_08_gis_microgrid_model.md            [proposed]
  stage_09_spatial_indexing.md               [proposed]
  stage_10_geospatial_representation.md      [proposed]
  stage_11_integration_and_outages.md        [proposed]
  stage_12_report_and_defense.md             [proposed]
  PROJECT_ROADMAP.md                        [this document]
  PROJECT_RECALL_PROMPT.md                   [context handoff]
```

### Reusable table of contents for future stage specifications

Use the following structure when drafting a missing stage. Preserve the existing Stage 00 and Stage 01 documents rather than rewriting them to match this template.

```markdown
# Stage NN: Title

## 1. Target and assignment connection
## 2. In scope and out of scope
## 3. Prerequisites and exact reading locations
## 4. Mathematical model, assumptions, and supported cases
## 5. Public APIs, data schemas, and command behavior
## 6. Small examples and independently established expected results
## 7. Algorithm and proof obligations, where applicable
## 8. Tests, reference checks, and experiments
## 9. Implementation order
## 10. Acceptance criteria and definition of done
## 11. Verification evidence and remaining limitations
## 12. At most five short lecturer questions and answers
```

Reference Stage 00 for permanent rules. Do not duplicate all policies in every stage document. State only stage-specific requirements and explicitly approved changes to shared contracts.

## 7. Working method and language rules

**Top-down teaching:** Start from the assignment target, identify what must be delivered, then consult only the relevant lecture or paper sections. Do not reteach the lectures from the beginning.

**Language:** Direct study discussion and explanations use Vietnamese and English. Repository documentation, source code, comments, docstrings, tests, CLI messages, implementation prompts, and implementation reports use English only.

**Defense preparation:** End each completed stage explanation with at most five short likely lecturer questions and answers. Use bilingual answers in teaching conversations and English in repository documents. A roadmap overview does not require repeating questions for every future stage.

**One stage at a time:** A target-only request to define a new stage produces its specification. An explicit implementation request uses the approved specification and stops at that stage boundary. A general request to recall the project does not authorize code changes.

The shared workflow is:

```text
Inspect -> clarify the contract -> design tests -> implement -> verify -> report -> stop
```

Stage 00 defines the reusable workflows `inspect-stage`, `implement-stage`, `verify-contract`, `design-tests`, `debug-regression`, and `review-handoff`. These are documented recipes, not proof that native editor skills or plugins have been installed. Guardrails are instructions; applicable tests, execution controls, and review provide additional checks.

## 8. Existing contracts to preserve

This is a recall summary. The detailed Stage 01 specification remains authoritative.

- Use Python 3.10-compatible code and `src/renewable_routing/`.
- Stage 01 and Stage 02 runtime code use only the standard library; `pytest` is the test dependency. Later dependencies require a stage-specific reason and declaration.
- Use frozen `Node`, `Edge`, and `FlowNetwork` dataclasses. Keep candidate flows separate and keyed by unique edge IDs.
- Use `outflow - inflow = Node.balance`: positive is required supply, negative is required consumption, zero is transit/inactive.
- Required balances sum to zero, but this does not establish that a feasible flow exists.
- Enforce `0 <= lower_capacity <= flow <= capacity`. Costs may be signed. Numeric values are integers excluding booleans; do not silently coerce or round.
- Preserve parallel and opposite-direction original edges separately. They are not automatically reverse residual arcs.
- Stage 01 rejects self-loops and permits isolated nodes, zero-capacity edges, and an empty edge list; at least one node is required.
- Keep `capacity` distinct from `unit_cost` and generation availability distinct from prescribed injection.
- Preserve `validate_network`, `validate_flow`, `evaluate_flow`, `load_network`, and `load_flow`, including the specified schemas and errors.
- Stage 01 has no optimization, feasibility search, or general infeasibility detector. A feasible candidate is not necessarily optimal; one failed candidate does not prove the network infeasible.
- Known fixtures: two-link flows `(5, 1)` cost 9 and `(3, 3)` cost 15; `(6, 0)` fails capacity; `(5, 0)` fails balance; transit flow costs 20.
- Stage 02 maximum-flow states use their own validated contract; do not force source/sink flow amounts to equal Stage 01's prescribed final balances.

Preserve unrelated work. Do not silently change policy, public contracts, schemas, or tests; expose secrets; add unapproved dependencies; download papers or datasets; perform destructive operations; commit; or push without the relevant authorization. Record actual results using appropriate labels such as PASS, FAIL, or NOT RUN.

## 9. Decisions still open

| Decision | Resolve by |
|---|---|
| Stage 03 solver initialization, negative-cost handling, and supported lower bounds | Before Stage 03 implementation. |
| Stage 04 method: cost scaling, network simplex, or another justified classical method | Before Stage 04 specification is finalized. |
| Definition and computation of the simplified minimum-ratio cycle and its correctness assumptions | Before Stage 05 implementation. |
| Independent reference solver, adapters, and approved dependencies | Start of solver validation, no later than Stage 03. |
| Benchmark graph families, capacity/cost ranges, repetitions, and timeout policy | Before Stage 07 measurements. |
| Region, geographic units, GIS layers, physical unit convention, and data permissions | Review availability early; finalize the Stage 08 contract. |
| Spatial-query distance metric, coordinate system, radius boundaries, and baseline | Before Stage 09 experiments. |
| Prediction target, labels, representation method, baseline, and evaluation split | Review label availability early; finalize Stage 10 before training. |
| Integrated solver choice and outage/partial-service policy | Before Stage 11 implementation. |

The second paper is a review that supports choosing one representation technique; it is not a requirement to implement every modality or an LLM-based system. No particular region, imagery model, or production infrastructure has been selected.

## 10. Continuation and progress handoff

### Minimal implementation request when the specification exists

```text
Implement Stage 01 according to docs/stage_01_problem_definition.md.
```

The agent must still read `AGENTS.md`, Stage 00, the active specification, and relevant current code/tests. The short prompt does not relax any guardrail.

### Define a stage before implementing it

```text
Define Stage 02.
Target: Residual networks, Ford-Fulkerson, and Edmonds-Karp with correctness tests.
Write the implementation specification only; do not implement code yet.
```

### Recall in a new conversation

Paste the prompt in [PROJECT_RECALL_PROMPT.md](PROJECT_RECALL_PROMPT.md), attach or make the relevant documents available, and fill in the active request. The prompt is a portable handoff, not persistent memory or proof of repository state.

### Progress block to update after an actual handoff

```text
Active stage:
Requested mode: discuss / define / implement / review
Last implementation verified:
Repository/branch/commit, if actually available:
Specification path:
Test commands and actual results:
Environment used:
Open blockers or decisions:
Next target:
```

Do not fill these fields from assumptions. If the repository is unavailable, state that implementation status is unverified and continue only with the accessible documentation task.

## 11. Sources and provenance

The assignment requirements and grading come from the Project 6 text supplied by the user in this conversation. Preserve that assignment as the requirements source; absence of a separate assignment PDF does not mean the requirements are unknown.

The current repository conventions and Stage 01 contract come from the supplied `README.md`, `AGENTS.md`, `docs/stage_00_repository_foundation.md`, and `docs/stage_01_problem_definition.md`. Stage numbering from 03 onward, the proposed first solver, and the future document names are planning choices introduced in this roadmap.

Supplied research/lecture files:

| File | Role and reading pointer |
|---|---|
| `Uploaded_Lecture07_graph_theory_advanced.pdf` | Stage 01 references: PDF pages 123-124, printed slides 113-114. Stage 02 discussion: PDF pages 128-142 and 150-155. These are maximum-flow foundations, not two complete minimum-cost-flow implementations. |
| `Uploaded_Lecture06_computational_geometry.pdf` | Spatial-search foundations for the GIS/indexing work. Select the relevant sections and verify exact PDF pages when preparing that stage; do not assume the slides implement PostGIS. |
| `[2025] Maximum Flow and Minimum-Cost Flow in Almost-Linear Time.pdf` | Paper 1, Chen et al. Formal problem: PDF page 2; contributions: pages 2-3. Use the actual paper for the later reduction outline, not a paraphrase of cycle canceling alone. |
| `[2025] Representation learning for geospatial data.pdf` | Paper 2, Liu et al. The assignment uses this review to select one geospatial representation technique for demand or generation estimation. |

Consult the actual supplied source for a source-specific explanation or proof, and cite its location. Filenames and this roadmap are not substitutes for inaccessible source content. Do not fetch online replacements for the supplied papers.
