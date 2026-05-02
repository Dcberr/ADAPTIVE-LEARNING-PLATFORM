# Recommendation Flow

## Overview

The recommendation flow starts from a minimal request:

- `student_id`
- `exercise_id`

The client does not send review or submission payloads. The service loads graph-backed context from Neo4j, lets the LLM decide what extra context is worth loading, lets the LLM decide the recommendation path, queries weighted exercise candidates from the graph, then lets the LLM choose the roadmap and build structured explanations with evidence refs.

The runtime graph is now organized as a set of subgraphs with explicit fallback nodes. This keeps the main workflow short while making each LLM-heavy phase resilient when parsing fails or the model returns weak output.

Model selection for these stages is also centralized by feature and stage in `app/config/model_config.py`, with environment-backed overrides resolved by `app/config/env_config.py`.
Prompt generation for recommendation stages is centralized under `app/prompts/recommendation/`.

## High-Level Flow

1. The client calls `POST /api/v1/recommendation`.
2. `context_subgraph` loads the minimum stable context and expands it conditionally.
3. `path_subgraph` decides `REINFORCE` or `IMPROVE`.
4. `roadmap_subgraph` queries weighted graph candidates and selects the final roadmap.
5. `explanation_subgraph` generates explanation blocks with structured refs.
6. The service stores `ASSIGNED` and `RECOMMENDS` relations for the final roadmap.

## Subgraph Layout

### Main Graph

The top-level `StateGraph(RecommendationState)` is intentionally small:

1. `context_subgraph`
2. `path_subgraph`
3. `roadmap_subgraph`
4. `explanation_subgraph`

Each subgraph owns one logical phase and can route to a fallback node without making the main graph hard to follow.

### `context_subgraph`

Nodes:

- `BaseContextLoader`
- `ContextPlanner`
- `ContextPlannerFallback`
- `ConditionalContextLoader`

Flow:

1. always load base context
2. ask the LLM which extra blocks are needed
3. if the planner output is valid, load those blocks
4. if the planner returns malformed non-JSON output, run one JSON-repair pass with the same stage model
5. if the repaired output is still invalid, route to `ContextPlannerFallback`
6. load a safe default block set

Stage model key:

- `recommendation.context_planner`

### `path_subgraph`

Nodes:

- `PathDecider`
- `PathDeciderFallback`

Flow:

1. ask the LLM for the assigned path and focus concept
2. if the result is valid, end the subgraph
3. otherwise route to the deterministic fallback path selector

Stage model key:

- `recommendation.path_decider`

### `roadmap_subgraph`

Nodes:

- `ExerciseCandidateRetriever`
- `RoadmapBuilder`
- `RoadmapBuilderFallback`

Flow:

1. query graph candidates deterministically
2. ask the LLM to choose the most important exercises
3. if the chosen ids map back to valid candidates, end the subgraph
4. otherwise route to the fallback that keeps the top graph candidates

Stage model key:

- `recommendation.roadmap_builder`

### `explanation_subgraph`

Nodes:

- `ExplanationBuilder`
- `ExplanationBuilderFallback`

Flow:

1. build an evidence catalog
2. ask the LLM for `reasoning` and `roadmap_summary`
3. if the explanation blocks are valid, end the subgraph
4. otherwise route to a templated evidence-backed fallback explanation

Stage model key:

- `recommendation.explanation_builder`

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

If the planner does not return a usable block list, the graph routes to `ContextPlannerFallback`, which loads a default mix of:

- `exercise_graph`
- `review_trend`
- `student_history`
- optionally `submission_trend`
- optionally `concept_progression`

Before that fallback happens, the service now makes one bounded JSON-repair attempt to recover malformed planner output into a single valid JSON object.

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

If the LLM output is invalid, `PathDeciderFallback` uses current errors, attempt regression, and review improvement to choose a safe default path.

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
- `difficulty_gap`
- `progression_score`
- `similarity_score`

### 6. RoadmapBuilder

The LLM receives the candidate list and chooses the most important exercises for the roadmap.

It returns:

- ordered `exercise_ids`
- step directives

The service resolves those ids back to the graph candidates. If the returned ids do not map to usable candidate exercises, `RoadmapBuilderFallback` keeps the top graph-ranked exercises and fills directives with deterministic defaults.

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

If the LLM output is empty or structurally invalid, `ExplanationBuilderFallback` returns a shorter but still evidence-backed explanation using the same ref catalog.

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

- [../architecture.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/architecture.md)
- [../domain/knowledge-graph.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/domain/knowledge-graph.md)
- [../api/recommendation-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/recommendation-api.md)
- [../api/review-import-api.md](/Users/thaibao/projects/review-code-app/codereviewai/docs/api/review-import-api.md)
