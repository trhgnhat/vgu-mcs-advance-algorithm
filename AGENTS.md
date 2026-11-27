# Coding Agent Instructions

Read these files before changing code:
1. README.md
2. docs/stage_00_repository_foundation.md
3. The implementation specification for the stage explicitly requested by the user.
4. .agents/skills/00_convention.md
5. .agents/skills/01_testing_convention.md

Inspect existing files and working-tree changes. Preserve unrelated work.
Use Python 3.10-compatible code. Keep repository content and implementation reports in English.
Implement only the active stage. The roadmap is not authorization to start future work.
Preserve public APIs, schemas, numerical conventions, and required tests.
Stage 1 validates supplied flows and evaluates cost; it does not implement a solver.
Use the named workflows in Stage 00 when appropriate.
Run applicable tests and examples; report actual results and anything not verified.
Do not download papers or datasets, add unapproved dependencies, expose secrets,
perform destructive actions, commit, or push without authorization.
This entrypoint does not replace the detailed Stage 00 and active-stage contracts.

## Testing Scope

- Organize runnable examples under `examples/stageN/` and tests under
  `tests/stageN/`.
- Prefer data-driven example evaluation and end-to-end stage behavior over a
  separate unit test for every function.
- Keep only tests required by the active-stage contract or a documented
  regression. Consolidate duplicate coverage when the same behavior remains
  verified.
- Preserve all explicitly required cases, mathematical invariants, error
  distinctions, and CLI exit codes.
- A simple demonstration is the normal concept-rerun path. Full stage and
  regression suites remain required during implementation and handoff.
- Follow `.agents/skills/01_testing_convention.md` for detailed test selection
  and verification.

## Standard Stage Execution

Apply this workflow whenever the user requests implementation of a stage.
The user does not need to repeat repository conventions or guardrails.

### Before editing

1. Read README.md and docs/stage_00_repository_foundation.md.
2. Identify the stage explicitly requested by the user.
3. Read its specification at docs/stage_NN_<topic>.md.
   Use the supplied path when available; otherwise locate the unique
   matching stage document.
4. If the specification is missing, ambiguous, or contradictory, report
   the blocker. Do not invent a contract or begin affected implementation.
5. Inspect relevant code, tests, configuration, and working-tree changes.
6. State a brief plan covering scope, affected files, and verification.

### During implementation

1. Apply Stage 00 conventions and the active stage's exact contracts.
2. Use inspect-stage before implementation.
3. Use verify-contract and design-tests for the affected requirements.
4. Use implement-stage to make the smallest complete change.
5. Use debug-regression when a test or existing behavior fails.
6. Preserve unrelated work and earlier-stage compatibility.
7. Do not change policy, specifications, or expected results merely to
   accommodate the implementation.

### Before completion

1. Run the active stage's required checks and applicable regression tests.
2. For documentation-only stages, run documentation checks; do not invent
   application-test results.
3. Review all changed and newly created files for scope violations.
4. Use review-handoff and evaluate the stage's definition of done.
5. Report:
   - Stage and scope.
   - Files changed.
   - Requirements completed.
   - Verification commands and actual results.
   - Environment used.
   - Unfinished or unverified requirements.
6. Stop at the requested stage boundary.

A request to implement one stage does not authorize the next stage.
A request to define or plan a stage authorizes documentation, not code.