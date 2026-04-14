# Recommendation Flow

## Overview

The recommendation flow is graph-backed and starts from a minimal request:

- `student_id`
- `exercise_id`

The client does not send the full review payload. The service loads the needed context from Neo4j.

## High-Level Flow

1. The client calls `POST /api/v1/recommendation`.
2. `RecommendationContextLoader` loads the latest stored review for `(student_id, exercise_id)`.
3. The same step loads recent review history through `NEXT_REVIEW_OF` and recent submission trend through `NEXT_ATTEMPT`.
4. `QueryPlanner` uses an LLM to choose a fixed query plan, start entity, target-concept hint, and path preference.
5. `PathSelector` combines planner preference with graph-backed rules to assign `REINFORCE`, `IMPROVE`, or `NEXT_CONCEPT`.
6. `TargetConceptSelector` chooses the target concept from the anchor concept, planner hint, and prerequisite graph.
7. `ExerciseCandidateRetriever` loads weighted exercise candidates from Neo4j.
8. `RoadmapBuilder` ranks candidates deterministically, with a small query-plan bias, and selects the roadmap.
9. `RecommendationExplainer` uses the LLM only to explain the already selected roadmap and stores assignment relations back into Neo4j.

## Detailed Flow

### 1. RecommendationContextLoader

Loads:

- latest stored `Review`
- recent `NEXT_REVIEW_OF` history
- latest `NEXT_ATTEMPT` trend
- stored `StudentProfileScoring`
- current concept and current concept weight
- mastered concepts
- attempted exercise ids

Derived state:

- `anchor_concept`
- `anchor_concept_weight`
- `critical_errors`
- `latest_review_improvement_signal`
- `latest_review_severity_change`
- `latest_submission_improvement_ratio`
- `latest_submission_regression_ratio`

### 2. QueryPlanner

The planner does not generate raw Cypher.

It chooses one fixed `query_plan_id` from:

- `review_reinforce_plan`
- `review_improve_plan`
- `concept_next_concept_plan`
- `submission_progress_plan`
- `exercise_related_plan`
- `full_progression_plan`

It also returns:

- `start_entity`
- `assigned_path`
- `target_concept_hint`
- `confidence`
- `rationale`

If planner output is weak or invalid, the flow falls back to a deterministic plan.

### 3. PathSelector

Inputs:

- latest review quality
- review trend
- submission trend
- student profile
- planner path suggestion

Process:

- compute `reinforce_score`
- compute `improve_score`
- compute `next_concept_score`
- choose the best path by score
- optionally keep the planner path when planner confidence is high and the planner choice is close enough to the best deterministic score

Outputs:

- `assigned_path`
- `framework.risk_level`
- `framework.readiness_level`

### 4. TargetConceptSelector

Default behavior:

- use `anchor_concept` as the target concept

For `NEXT_CONCEPT`:

- query next concepts from `PREREQUISITE_OF`
- score them with prerequisite strength, best next-path support, and learner readiness
- choose the highest scoring concept

If planner gives a concept hint for non-`NEXT_CONCEPT` paths:

- use the planner hint as the focus concept

### 5. ExerciseCandidateRetriever

Loads candidate exercises from Neo4j for:

- current exercise
- focus concept
- assigned path

Signals loaded per candidate:

- `path_weight`
- `tests_weight`
- `related_weight`
- `relation_type`
- `difficulty_gap`
- `progression_score`
- `similarity_score`

### 6. RoadmapBuilder

For each candidate:

- compute graph score from weighted graph relations
- compute student profile adjustment
- apply a small planner-based query-plan bias
- combine them into final score

Then:

- sort candidates by `final_score`
- keep top unique exercises
- choose up to 3 roadmap steps
- compute `graph_summary` from the best candidate and recent trend signals

### 7. RecommendationExplainer

The LLM is used only after the roadmap is already selected.

It generates:

- `reasoning`
- `roadmap_summary`
- per-step `directive`

If the LLM response is weak or invalid, fallback text is used.

## Main Inputs

- latest review
- recent review history
- recent submission trend
- student profile
- planner decision over fixed query plans
- exercise-to-concept graph links
- exercise-to-exercise related links
- concept prerequisite graph
- recommendation path graph links
- related-exercise metadata such as relation type, difficulty gap, progression score, and similarity score
- review-history metadata such as `same_concept`, `improvement_signal`, and `severity_change`

## Main Outputs

- anchor concept
- assigned recommendation path
- focus concept id
- graph summary metrics
- ordered exercise roadmap
- stored `ASSIGNED` relations for the student

Roadmap item shape:

- `step`
- `exercise.exercise_id`
- `exercise.title`
- `exercise.description`
- `exercise.content`
- `exercise.difficulty`
- `exercise.tags`
- `exercise.concept_ids`
- `exercise.directive`

## Related Docs

- [../architecture.md](/Users/thaibao/projects/review-code-app/review-agent/docs/architecture.md)
- [../domain/knowledge-graph.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/knowledge-graph.md)
- [../domain/recommendation-formulas.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/recommendation-formulas.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-import-api.md)
