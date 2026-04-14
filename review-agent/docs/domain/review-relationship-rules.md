# Review Relationship Rules

## Overview

This document defines the domain rules for `Review` relationships in the knowledge graph.

It focuses on:

- `Student -> Review`
- `Submission -> Review`
- `Review -> Submission`
- `Review -> Exercise`
- `Review -> Review`

## Source Of Truth

For the review write flow:

- the request provides:
  - `submission_id`
  - `summary`
  - `detail`
  - `review_items`
  - `scorecard`
  - optional `current_concept`
- Neo4j validates that the referenced `Submission` already exists
- `student_id` and `exercise_id` are derived from the linked submission
- review-history links are derived from stored reviews for the same student

## Rule 1. `RECEIVED_REVIEW` From Student

Relation:

- `(:Student)-[:RECEIVED_REVIEW]->(:Review)`

Domain rule:

- this relation is owned by the review write API
- it is refreshed on every review write
- the student is derived from the linked submission, not supplied separately in the request

Meaning:

- identifies which learner the review belongs to
- allows recommendation to load the latest review for a student

## Rule 2. `RECEIVED_REVIEW` From Submission

Relation:

- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`

Domain rule:

- this relation is owned by the review write API
- the request must resolve to an existing submission
- it is refreshed on every review write

Meaning:

- binds one review result to the exact submission it evaluates

## Rule 3. `REVIEWS_SUBMISSION`

Relation:

- `(:Review)-[:REVIEWS_SUBMISSION]->(:Submission)`

Domain rule:

- this relation is owned by the review write API
- it is refreshed together with `Submission -> RECEIVED_REVIEW`

Meaning:

- supports traversal from review back to the exact attempt

## Rule 4. `REVIEWS_EXERCISE`

Relation:

- `(:Review)-[:REVIEWS_EXERCISE]->(:Exercise)`

Domain rule:

- the exercise is derived from the linked submission
- if the submission is linked to an exercise, the review write API refreshes this relation
- the request does not create or override exercise ownership directly

Meaning:

- lets recommendation connect review findings to exercise-level concept and roadmap links

## Rule 5. `NEXT_REVIEW_OF`

Relation:

- `(:Review)-[:NEXT_REVIEW_OF {student_id, linked_at, same_concept, improvement_signal, severity_change}]->(:Review)`

Domain rule:

- this relation is owned by the review write API
- it links adjacent reviews for the same student by `created_at`
- if a stored review is patched again, both incoming and outgoing adjacent links around it are rebuilt

Meaning:

- `student_id`: owner of the review chain
- `linked_at`: when the chain relation was refreshed
- `same_concept`: whether the two reviews focus on the same concept id
- `improvement_signal`: overall positive learning movement from previous review to next review
- `severity_change`: change in issue severity from previous review to next review

## Scoring Rule

`NEXT_REVIEW_OF` scoring blends scorecard progress with issue severity reduction.

Intermediate values:

- `previous_average_score`: average `scorecard[*].score` on the previous review
- `current_average_score`: average `scorecard[*].score` on the current review
- `normalized_score_delta = (current_average_score - previous_average_score) / 4`
- `previous_severity`: average issue severity from `review_items`
- `current_severity`: average issue severity from `review_items`

Issue severity mapping:

- `Error` -> `1.0`
- `Warning` -> `0.5`
- any other item type -> `0.25`

Final scores:

- `improvement_signal = 0.6 * max(normalized_score_delta, 0) + 0.4 * max(previous_severity - current_severity, 0)`
- `severity_change = current_severity - previous_severity`

Interpretation:

- high `improvement_signal` means the newer review shows better scorecard quality and/or less severe issues
- `severity_change < 0` means the newer review is less severe
- `severity_change > 0` means the newer review became more severe

## Write Rule

The review API is a full upsert:

- all request fields are required
- the request overwrites the stored review fields for that `review_id`
- relation sets owned by the review are rebuilt from the final stored state

## Recommendation Usage

Recommendation can use review relations to answer:

- what is the latest feedback for this exercise?
- is the student improving across recent reviews?
- is the learner still struggling with the same concept?

Typical signals:

- high `improvement_signal` and low issue severity -> supports `IMPROVE` or `NEXT_CONCEPT`
- negative `severity_change` -> supports progress-aware encouragement
- repeated `same_concept = true` chains with weak improvement -> supports `REINFORCE`

## Maintenance Rule

If the review API changes any of these:

- relation ownership
- full overwrite behavior
- review-history linking behavior
- review progression scoring

then this document must be updated together with:

- `docs/api/review-import-api.md`
- `docs/workflows/knowledge-graph-flow.md`
- `docs/workflows/recommendation-flow.md`
- `docs/domain/knowledge-graph.md`
- `docs/architecture.md` when system behavior changes
