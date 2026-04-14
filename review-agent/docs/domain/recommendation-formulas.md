# Recommendation Formulas

## Overview

This document defines the current formulas used by the recommendation flow.

It covers:

- path scoring
- framework label mapping
- target concept scoring
- candidate graph scoring
- student profile adjustment
- planner bias
- final roadmap ranking

These formulas reflect the current implementation in `app/services/recommendation_service.py`.

## 1. Score Normalization

Review scorecard values use `1..5`.

They are normalized with:

```text
normalized_score = (score - 1) / 4
```

Range:

- `0.0` to `1.0`

## 2. Path Scoring

Definitions:

- `error_pressure = min(critical_errors / 3, 1.0)`
- `scorecard_average = average(normalized scorecard values)`
- `review_improve = latest_review_improvement_signal`
- `review_severity_drop = max(-latest_review_severity_change, 0.0)`
- `submission_improve = latest_submission_improvement_ratio`
- `submission_regress = latest_submission_regression_ratio`
- `cm = concept_mastery`
- `di = debugging_independence`
- `ct = concept_transfer`
- `lv = learning_velocity`

### REINFORCE

```text
reinforce_score =
  0.35 * error_pressure
+ 0.20 * (1 - scorecard_average)
+ 0.20 * submission_regress
+ 0.15 * review_severity_drop
+ 0.10 * max(0, 0.6 - di)
```

### IMPROVE

```text
improve_score =
  0.30 * review_improve
+ 0.25 * submission_improve
+ 0.20 * min(critical_errors / 2, 1.0)
+ 0.15 * (1 - abs(scorecard_average - 0.6))
+ 0.10 * (1 - max(cm - 0.7, 0.0))
```

### NEXT_CONCEPT

```text
next_concept_score =
  0.30 * scorecard_average
+ 0.25 * review_improve
+ 0.20 * submission_improve
+ 0.15 * cm
+ 0.10 * lv
- 0.20 * error_pressure
```

Path selection:

```text
assigned_path = argmax(
  reinforce_score,
  improve_score,
  next_concept_score
)
```

## 3. Planner Override Rule

Planner provides:

- `assigned_path`
- `confidence`

If:

- `planner_confidence >= 0.6`
- and `planned_score + 0.15 >= best_deterministic_score`

then the planner path can replace the best deterministic path.

## 4. Framework Label Mapping

### Risk Level

- `high` if `reinforce_score >= 0.55`
- `low` if `next_concept_score >= 0.55` and `error_pressure < 0.2`
- otherwise `medium`

### Readiness Level

- `ready` if `next_concept_score >= 0.6`
- `emerging` if `reinforce_score >= 0.55`
- otherwise `developing`

## 5. Target Concept Scoring

Default:

- `target_concept = anchor_concept`

For `NEXT_CONCEPT`, each next concept is scored with:

```text
readiness = (cm + ct + lv) / 3

target_concept_score =
  0.50 * prerequisite_strength
+ 0.30 * best_path_weight
+ 0.20 * readiness
```

Pick the highest scoring next concept.

## 6. Candidate Graph Scoring

Definitions:

- `path_fit = RECOMMENDED_FOR.weight`
- `concept_fit = TESTS.weight`
- `related_fit = RELATED_TO.weight`
- `progression_fit = RELATED_TO.progression_score`
- `similarity_fit = RELATED_TO.similarity_score`
- `difficulty_gap = RELATED_TO.difficulty_gap`

Helpers:

```text
easier_fit = 1 - max(difficulty_gap, 0.0)
moderate_fit = 1 - abs(difficulty_gap - 0.3)
next_step_fit = 1 - abs(difficulty_gap - 0.5)
```

### REINFORCE Candidate

```text
graph_score =
  0.35 * path_fit
+ 0.25 * concept_fit
+ 0.20 * related_fit
+ 0.15 * similarity_fit
+ 0.05 * easier_fit
```

### IMPROVE Candidate

```text
graph_score =
  0.30 * path_fit
+ 0.25 * concept_fit
+ 0.20 * progression_fit
+ 0.15 * related_fit
+ 0.10 * moderate_fit
```

### NEXT_CONCEPT Candidate

```text
graph_score =
  0.35 * path_fit
+ 0.25 * concept_fit
+ 0.20 * progression_fit
+ 0.10 * next_step_fit
+ 0.10 * max(related_fit, 0.2)
```

Clamp to `0.0..1.0`.

## 7. Student Profile Adjustment

### REINFORCE

```text
profile_adjustment =
  0.40 * (1 - debugging_independence)
+ 0.30 * (1 - implementation_consistency)
+ 0.30 * easier_fit
```

### IMPROVE

```text
profile_adjustment =
  0.35 * implementation_consistency
+ 0.35 * debugging_independence
+ 0.30 * concept_transfer
```

### NEXT_CONCEPT

```text
profile_adjustment =
  0.40 * concept_mastery
+ 0.30 * concept_transfer
+ 0.30 * learning_velocity
```

## 8. Planner Query-Plan Bias

The planner does not directly execute raw Cypher.

Instead, its chosen fixed plan adds a small ranking bias.

### `review_reinforce_plan`

```text
+ 0.10 * similarity_score
+ 0.05 * related_weight
```

### `review_improve_plan`

```text
+ 0.08 * progression_score
+ 0.05 * related_weight
```

### `concept_next_concept_plan`

```text
+ 0.10 * path_weight
+ 0.05 * max(difficulty_gap, 0.0)
```

### `submission_progress_plan`

```text
+ 0.08 * latest_submission_improvement_ratio
+ 0.05 * progression_score
```

### `exercise_related_plan`

```text
+ 0.12 * related_weight
+ 0.06 * similarity_score
```

### `full_progression_plan`

```text
+ 0.05 * latest_review_improvement_signal
+ 0.05 * latest_submission_improvement_ratio
```

Clamp adjusted graph score to `0.0..1.0`.

## 9. Final Candidate Score

```text
final_score =
  0.75 * graph_score
+ 0.25 * profile_adjustment
```

After planner bias is applied, clamp to `0.0..1.0`.

## 10. Roadmap Selection

Process:

1. rank candidates by:
   - `final_score`
   - `path_weight`
   - `related_weight`
   - `progression_score`
2. keep top unique exercises
3. select up to 3 roadmap steps

## 11. Graph Summary Metrics

The current response returns:

- `current_concept_weight`
- `best_path_weight`
- `best_related_exercise_weight`
- `latest_review_improvement_signal`
- `latest_review_severity_change`
- `latest_submission_improvement_ratio`
- `latest_submission_regression_ratio`

These are taken from the current context and the best ranked candidate.

## 12. Response Concept Fields

The recommendation response exposes:

- `focus_concept_id`
- `concept_ids`

Rules:

- `focus_concept_id` is the final selected concept used by the flow internally
- `concept_ids` is loaded from Neo4j node data by reading the selected exercise nodes and their outgoing `TESTS` concept links
- `concept_ids` is ordered by the maximum `TESTS.weight` seen across the selected roadmap exercises
- if `focus_concept_id` is not present in the collected concept list, it is inserted at the front of the response list

## Maintenance Rule

If recommendation code changes any of these:

- path scoring
- planner override logic
- target concept scoring
- graph candidate scoring
- student profile adjustment
- planner bias
- roadmap ranking

then this document must be updated together with:

- `docs/workflows/recommendation-flow.md`
- `docs/api/recommendation-api.md`
- `docs/architecture.md` when system behavior changes
