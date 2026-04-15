# Recommendation Flow

## Overview

The recommendation flow starts from a minimal request:

- `student_id`
- `exercise_id`

The client does not send review or submission payloads. The service loads graph-backed context from Neo4j, lets the LLM decide what extra context is worth loading, lets the LLM decide the recommendation path, queries weighted exercise candidates from the graph, then lets the LLM choose the roadmap and build structured explanations with evidence refs.

## High-Level Flow

1. The client calls `POST /api/v1/recommendation`.
2. `BaseContextLoader` loads the minimum stable context from Neo4j.
3. `ContextPlanner` uses the LLM to decide which extra context blocks are needed.
4. `ConditionalContextLoader` fetches only those selected context blocks.
5. `PathDecider` uses the LLM to choose `REINFORCE`, `IMPROVE`, or `NEXT_CONCEPT`.
6. `ExerciseCandidateRetriever` queries weighted graph candidates for the selected path.
7. `RoadmapBuilder` uses the LLM to filter the most important exercises and build the roadmap.
8. `ExplanationBuilder` uses the LLM to generate explanation blocks with structured refs.
9. The service stores `ASSIGNED` and `RECOMMENDS` relations for the final roadmap.

## Detailed Flow

### 1. BaseContextLoader

Always loads:

- current `Exercise`
- strongest `TESTS` concepts for that exercise
- current exercise `RECOMMENDED_FOR` links
- latest stored `Review` for `(student_id, exercise_id)`
- latest stored `Submission` for `(student_id, exercise_id)`
- stored `StudentProfileScoring`
- mastered concept ids
- attempted exercise ids

Derived state:

- `anchor_concept`
- `anchor_concept_weight`
- `critical_errors`
- initial `focus_concept_id`

### 2. ContextPlanner

The planner does not generate Cypher.

It chooses which extra context blocks to fetch next from this fixed set:

- `review_trend`
- `submission_trend`
- `exercise_graph`
- `concept_progression`
- `student_history`

It also returns:

- `provisional_focus_concept_id`
- `priority_signal`
- `reason`

### 3. ConditionalContextLoader

Loads only the selected extra blocks.

Possible graph reads:

- `NEXT_REVIEW_OF` history and transition scores
- `NEXT_ATTEMPT` transition scores
- current exercise `RELATED_TO` neighborhood
- next-concept candidates from `PREREQUISITE_OF`
- attempted and assigned exercise history

This stage also loads previous review and previous submission payloads when available so the explanation step can cite them later.

### 4. PathDecider

The LLM reads the assembled context and returns:

- `assigned_path`
- `focus_concept_id`
- `confidence`
- `risk_level`
- `readiness_level`
- `reason`

The decision is constrained to:

- `REINFORCE`
- `IMPROVE`
- `NEXT_CONCEPT`

### 5. ExerciseCandidateRetriever

The service queries weighted exercise candidates from Neo4j using:

- current exercise id
- anchor concept
- chosen focus concept
- chosen path
- attempted exercise ids

Graph signals returned per candidate include:

- `path_weight`
- `tests_weight`
- `related_weight`
- `relation_type`
- `difficulty_gap`
- `progression_score`
- `similarity_score`

### 6. RoadmapBuilder

The LLM receives the candidate list and chooses the most important exercises for the roadmap.

It returns:

- ordered `exercise_ids`
- step directives

The service resolves those ids back to the graph candidates and falls back to the top graph candidates if the LLM selection is weak or invalid.

### 7. ExplanationBuilder

The explanation stage is evidence-backed.

It builds a ref catalog from:

- current review
- previous review
- current submission code snippet
- previous submission code snippet
- current exercise
- selected roadmap exercises

The LLM then returns:

- `reasoning.content`
- `reasoning.refs`
- `roadmap_summary.content`
- `roadmap_summary.refs`

Each explanation block uses placeholders like `{ref_review_current}` in the content, and each referenced item is returned separately with:

- `ref_id`
- `content`
- `ref_category`

Allowed `ref_category` values:

- `code`
- `review`
- `exercise`

## Main Inputs

- latest review
- latest submission
- student profile
- current exercise concept links
- LLM context-plan decision
- LLM path decision
- weighted exercise candidates from Neo4j
- previous review and submission evidence for explanation

## Main Outputs

- anchor concept
- assigned recommendation path
- focus concept id
- graph summary metrics
- ordered exercise roadmap
- explanation blocks with structured refs
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
- [../api/recommendation-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/recommendation-api.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-import-api.md)
