# Submission Progression Rules

## Overview

This document defines the domain rules for submission relationships and attempt progression scoring.

It focuses on:

- `Student -> Submission`
- `Submission -> Exercise`
- `Submission -> Review`
- `Submission -> Submission`

## Source Of Truth

For the submission write flow:

- the request provides:
  - `student_id`
  - `exercise_id`
  - `code`
  - `testcase_outputs`
- Neo4j validates that `Student` and `Exercise` already exist
- progression links are derived from stored submissions for the same student and exercise

## Rule 1. `SUBMITTED`

Relation:

- `(:Student)-[:SUBMITTED]->(:Submission)`

Domain rule:

- the request must carry `student_id`
- that student must already exist
- the relation is refreshed on every submission write

Meaning:

- identifies the owner of the submission

## Rule 2. `FOR_EXERCISE`

Relation:

- `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`

Domain rule:

- the request must carry `exercise_id`
- that exercise must already exist
- the relation is refreshed on every submission write

Meaning:

- identifies which exercise the attempt belongs to

## Rule 3. `RECEIVED_REVIEW` and `REVIEWS_SUBMISSION`

Relations:

- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Review)-[:REVIEWS_SUBMISSION]->(:Submission)`

Domain rule:

- these are created by the review write API, not the submission write API
- the submission must already exist before review import can succeed

Meaning:

- bind one review result to one submission

## Rule 4. `NEXT_ATTEMPT`

Relation:

- `(:Submission)-[:NEXT_ATTEMPT {student_id, linked_at, same_exercise, improvement_ratio, regression_ratio}]->(:Submission)`

Domain rule:

- this relation is refreshed by the submission write API
- it links adjacent attempts by the same student on the same exercise
- if a past submission is patched again, the adjacent links around it are rebuilt

Meaning:

- `student_id`: owner of the attempt chain
- `linked_at`: when the relation was refreshed
- `same_exercise`: whether the chain stays on the same exercise
- `improvement_ratio`: how much the next attempt improved
- `regression_ratio`: how much the next attempt got worse

## Scoring Rule

Progress scores are computed from `testcase_outputs`.

Testcase pass rule:

- a testcase is treated as passed when:
  - `expect.strip() == output.strip()`

Derived sets:

- `previous_failed`: failed testcase indexes in the previous submission
- `current_failed`: failed testcase indexes in the current submission

Intermediate values:

- `fixed_count = len(previous_failed - current_failed)`
- `newly_broken_count = len(current_failed - previous_failed)`
- `previous_pass_rate = passed_previous / total_previous`
- `current_pass_rate = passed_current / total_current`

Final scores:

- `improvement_ratio` blends positive pass-rate delta with fixed testcase ratio
- `regression_ratio` blends negative pass-rate delta with newly broken testcase ratio

Interpretation:

- high `improvement_ratio` means the student fixed important failures between attempts
- high `regression_ratio` means the newer attempt introduced or reopened failures

## Validation Rule

If either relation source entity is missing:

- missing `student_id` -> submission API returns `404`
- missing `exercise_id` -> submission API returns `404`

The submission API does not create placeholder student or exercise nodes from relation ids.

## Recommendation Usage

Recommendation and analytics can use `NEXT_ATTEMPT` to answer:

- Is the student improving on this exercise?
- Is the learner stuck on the same concept area?
- Did the newest attempt regress?

Typical signals:

- high `improvement_ratio` -> supports `IMPROVE` or `NEXT_CONCEPT`
- high `regression_ratio` -> supports `REINFORCE`

## Maintenance Rule

If the submission API changes any of these:

- relation validation behavior
- `NEXT_ATTEMPT` linking behavior
- progression score formula
- testcase comparison rule

then this document must be updated together with:

- `docs/api/review-import-api.md`
- `docs/workflows/knowledge-graph-flow.md`
- `docs/architecture.md` when system behavior changes
