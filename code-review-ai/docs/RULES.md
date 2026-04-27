# Documentation Update Rules

## Purpose

This file defines the minimum documentation update rules that should be followed whenever code changes are made.

The goal is to keep code, APIs, workflows, domain meaning, and examples synchronized so coding agents and teammates can trust the docs.

## Global Rule

When code is updated, the related docs must be updated in the same change whenever the behavior, contract, structure, or meaning has changed.

Do not treat documentation as optional follow-up work.

When requirements change, tests must be considered part of the same change.

Before modifying code, always look for the most relevant existing documentation first.

This means:

- find the closest matching API doc if you are changing an endpoint
- find the closest matching domain doc if you are changing graph, scoring, or model meaning
- find the closest matching workflow doc if you are changing execution flow
- find the closest matching architecture doc if you are changing top-level structure
- find the closest matching test files before changing logic, validation, prompt behavior, or orchestration

Do not make code changes first and only later try to guess which docs matter.
Start by locating the related docs, then keep them aligned with the implementation.

## Update Rules By Change Type

### 1. API Changes

If you change:

- route path
- HTTP method
- request schema
- response schema
- validation behavior
- persistence behavior
- graph-write behavior

Then you must update:

- the matching file in `docs/api/`
- `docs/api/README.md` if a new API doc is added, removed, or renamed
- example payloads inside that API doc

Examples:

- update `docs/api/concept-api.md` when concept request fields change
- update `docs/api/review-import-api.md` when submission or review endpoints change
- update `docs/api/review-code-api.md` when the review request or response changes

### 2. Domain Model Changes

If you change:

- graph entities
- graph relationships
- relationship weights
- scoring meanings
- normalized ranges
- domain concepts or terminology

Then you must update:

- the matching file in `docs/domain/`
- `docs/domain/README.md` if a new domain doc is added, removed, or renamed

Examples:

- update `docs/domain/knowledge-graph.md` when Neo4j relationships change
- update `docs/domain/concept-weight-rules.md` when prerequisite or concept weights change
- update `docs/domain/exercise-recommendation-rules.md` when exercise relation validation or recommendation-facing exercise rules change
- update `docs/domain/submission-progression-rules.md` when submission relation behavior or progression scoring changes
- update `docs/domain/student-profile-scoring.md` when profile scoring ranges or semantics change

### 3. Workflow Changes

If you change:

- execution order
- routing conditions
- agent responsibilities
- service orchestration
- data handoff between steps

Then you must update:

- the matching file in `docs/workflows/`
- `docs/workflows/README.md` if a workflow doc is added, removed, or renamed

Examples:

- update `docs/workflows/codereviewai.md` when the review graph changes
- update `docs/workflows/recommendation-flow.md` when recommendation orchestration changes
- update `docs/workflows/knowledge-graph-flow.md` when graph write flow changes

### 4. Architecture Changes

If you change:

- system structure
- major dependency wiring
- top-level flow between subsystems
- major startup/runtime responsibilities

Then you must update:

- `docs/architecture.md`
- `docs/README.md` if the navigation structure changes

### 5. Example Changes

If you change:

- example request bodies
- example response bodies
- example entity shapes
- common payload conventions

Then you must update:

- inline examples in the relevant API docs
- `docs/examples/README.md` if the examples folder structure changes
- any future example JSON files under `docs/examples/`

### 6. Test Changes

If you change:

- requirements
- business rules
- function behavior
- routing logic
- prompt logic
- validation behavior
- scoring or ranking behavior

Then you must:

- find the most relevant existing test files first
- update the matching tests in the same change when current expectations are no longer correct
- add new tests when the changed behavior is not already covered
- run the most relevant tests for the modified function, module, or workflow after making the change
- if those relevant tests fail, iterate on the code and re-run the relevant tests
- limit that fix-and-retest loop to at most 5 attempts before reporting the remaining failure clearly

If tests cannot be run, say so clearly in the final update.

## Required Mapping

Use this mapping when deciding what must be updated:

- API contract change -> update `docs/api`
- Core meaning or graph rule change -> update `docs/domain`
- Execution flow change -> update `docs/workflows`
- System-level structure change -> update `docs/architecture.md`
- Payload/example change -> update examples too
- Requirement or behavior change -> update related tests too

## Minimum Review Checklist

Before finishing a code change, check:

1. Did any request or response shape change?
2. Did any graph node, relation, or weight meaning change?
3. Did any agent or workflow step change?
4. Did any example payload become outdated?
5. Does `docs/README.md` still point to the right files?
6. Did any requirement or function behavior change that should update or add tests?
7. Did I run the most relevant tests for the changed code?

If the answer is yes to any of these, update the related docs before closing the task.

## Rule For Coding Agents

When modifying code:

- first find the most relevant existing documentation
- first find the most relevant existing tests for the affected code path
- always identify whether the change affects `api`, `domain`, `workflows`, `architecture`, or `examples`
- update the matching docs in the same task
- update or add matching tests in the same task when behavior changed
- after modifying code, run the most relevant tests for the changed function, module, or workflow
- if relevant tests fail, modify the code and re-run the relevant tests before closing the task
- retry that code-fix and test cycle at most 5 times
- if a new doc category is introduced, update the relevant `README.md` index file too

If multiple docs are related, prefer updating all directly affected docs rather than only the closest one.

If a matching domain rule document does not exist yet for the changed behavior, create it in `docs/domain/` as part of the same task.

Priority for finding related docs:

1. exact endpoint doc in `docs/api`
2. exact workflow doc in `docs/workflows`
3. exact domain meaning doc in `docs/domain`
4. `docs/architecture.md`
5. `docs/README.md` and folder `README.md` index files when navigation changes

Priority for finding related tests:

1. exact test file for the changed function or module
2. exact workflow or API test for the affected behavior
3. broader integration tests that cover the changed path

## Practical Principle

Code and docs should describe the same system version.

If one changes, the other should change in the same commit or patch whenever possible.

Code, docs, and tests should describe the same system version.

If requirements change, update all three whenever possible.
