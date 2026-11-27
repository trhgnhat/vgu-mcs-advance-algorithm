# Stage Testing Convention

Read this convention after `00_convention.md` and the active-stage
specification. A stage specification takes precedence when it requires
particular cases or verification commands.

## Purpose

Keep tests small, stage-local, and focused on observable data outcomes. Tests
support implementation and demonstration; they should not mirror every helper
function or internal branch.

## Stage Layout

For each implemented stage `N`, prefer:

```text
examples/stageN/                 # Small input data and a runnable demonstration
tests/stageN/test_example_cases.py
tests/stageN/test_contract.py    # Only when the stage has additional contracts
tests/stageN/test_cli.py         # Only when the stage exposes a CLI
```

Do not create directories or placeholders for future stages before their
specifications are approved.

## Test Selection

- Start with independently derived example outcomes and end-to-end behavior.
- Keep every test traceable to an active-stage requirement or a real regression.
- Group related cases in one data-driven test when separate functions add no
  clarity.
- Test public behavior rather than private helpers or implementation details.
- Avoid duplicate assertions already exercised by the same example path.
- Preserve every explicitly required case, error distinction, exit code, and
  compatibility contract even when consolidating tests.
- Add focused unit tests only when an end-to-end case cannot isolate an
  important mathematical invariant or boundary.

For algorithm stages, demonstrations should show the input, independently
known result, important intermediate explanation when required, and final
outcome. A demonstration does not replace required correctness or reference
checks.

## Verification

During ordinary concept study, run the stage demonstration:

```bash
python examples/stageN/run_cases.py
```

During implementation or handoff, run both the stage tests and the applicable
regression suite:

```bash
python -m pytest -q tests/stageN
python -m pytest -q
```

Report actual results. Do not call a demonstration pass proof of untested
general correctness, optimality, or performance.
