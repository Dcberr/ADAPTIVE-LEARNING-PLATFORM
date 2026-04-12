# Concept Weight Rules

## Overview

This document defines how concept-related weights should be interpreted in the knowledge graph.

It focuses on weights used for:

- concept prerequisites
- exercise-to-concept coverage
- exercise-to-exercise relatedness
- exercise recommendation fit by concept and path
- student-to-concept concept-state scoring

These rules help recommendation stay consistent when ranking:

- what the student should reinforce
- what the student should improve
- when the student is ready for the next concept

## 1. `PREREQUISITE_OF.strength`

Relation:

- `(:Concept)-[:PREREQUISITE_OF {strength}]->(:Concept)`

Purpose:

- represent how necessary the prerequisite concept is before learning the target concept

Meaning:

- `1.0`: hard prerequisite
- `0.6`: strong supporting prerequisite
- `0.3`: soft prerequisite

Interpretation:

- `1.0` means the student usually should not move forward without enough mastery in the prerequisite
- `0.6` means the prerequisite is strongly helpful and should influence recommendation, but is not always blocking
- `0.3` means the prerequisite is useful context only and should have lighter impact

How to use in recommendation:

- if a weak prerequisite has `strength = 1.0`, prefer `REINFORCE`
- if a weak prerequisite has `strength = 0.6`, `IMPROVE` may still be acceptable depending on other signals
- if only `0.3` prerequisites are weak, `NEXT_CONCEPT` can still be reasonable

## 2. `TESTS.weight`

Relation:

- `(:Exercise)-[:TESTS {weight}]->(:Concept)`

Purpose:

- represent how strongly an exercise evaluates a concept

Meaning:

- `1.0`: main concept of the exercise
- `0.5` to `0.8`: important supporting concept
- `0.1` to `0.4`: minor supporting concept

Interpretation:

- high weight means performance on the exercise is strong evidence about that concept
- low weight means the concept is present but should not dominate recommendation decisions

Authoring note:

- the exercise upsert API can evaluate this weight with the knowledge-graph LLM from the exercise and concept metadata

How to use in recommendation:

- prioritize exercises where the target concept has the highest `TESTS.weight`
- avoid treating minor concept links as primary evidence of mastery or struggle

## 3. `RELATED_TO.weight`

Relation:

- `(:Exercise)-[:RELATED_TO {weight}]->(:Exercise)`

Purpose:

- represent how strongly two exercises should be treated as close neighbors for recommendation or curriculum navigation
- capture why they are related and whether the target is a better next step or just similar practice

Meaning:

- `1.0`: very close sibling or follow-up exercise
- `0.5` to `0.8`: useful related practice
- `0.1` to `0.4`: weak similarity or optional extension

Interpretation:

- high weight means the target exercise is a strong nearby candidate when the learner needs more practice around the same area
- low weight means the relation can help discovery but should not dominate ranking

Authoring note:

- the exercise upsert API can evaluate this weight with the knowledge-graph LLM from the main exercise and related exercise metadata

How to use in recommendation:

- boost exercises related to the current exercise when the concept focus still matches the learner need
- do not let `RELATED_TO.weight` override stronger concept-state or path-fit evidence

Recommended supporting fields on the same relation:

- `relation_type`: why the relation exists
- `target_concept_id`: main concept explaining the relation
- `shared_concept_ids`: concepts both exercises share
- `difficulty_gap`: difficulty jump from source to target
- `progression_score`: how good the target is as a next step
- `similarity_score`: how close the exercises are in concept/task shape

## 4. `RECOMMENDED_FOR.weight`

Relation:

- `(:Exercise)-[:RECOMMENDED_FOR {path, weight}]->(:Concept)`

Purpose:

- represent how well an exercise fits a recommendation path for a concept

Meaning:

- `1.0`: very strong fit for that path and concept
- `0.5` to `0.8`: useful fit
- `0.1` to `0.4`: weak fit

Interpretation:

- a high-weight `REINFORCE` edge means the exercise is especially good for rebuilding that concept
- a high-weight `NEXT_CONCEPT` edge means the exercise is a strong bridge into the next topic

How to use in recommendation:

- rank candidate exercises by `RECOMMENDED_FOR.weight`
- combine this weight with `TESTS.weight` and student concept state

## 5. `HAS_CONCEPT_STATE` Weights

Relation:

- `(:Student)-[:HAS_CONCEPT_STATE {mastery_score, struggle_score, confidence, evidence_count, updated_at}]->(:Concept)`

Purpose:

- store the student's concept-specific learning state

Meaning:

- `mastery_score`: how ready the student is to move forward on this concept
- `struggle_score`: how strongly the student still needs reinforcement on this concept
- `confidence`: how reliable the scores are
- `evidence_count`: how much review/submission evidence supports the relation

Suggested ranges:

- `mastery_score`: `0.0` to `1.0`
- `struggle_score`: `0.0` to `1.0`
- `confidence`: `0.0` to `1.0`

Interpretation:

- high `mastery_score` and low `struggle_score` means likely ready for `NEXT_CONCEPT`
- high `struggle_score` means likely needs `REINFORCE`
- medium scores on both often indicate `IMPROVE`

Suggested thresholds:

- `MASTERED` interpretation:
  - `mastery_score >= 0.75`
  - `struggle_score < 0.35`
- `STRUGGLES_WITH` interpretation:
  - `struggle_score >= 0.60`

## 6. Best Combined Ranking Logic

For concept-targeted recommendation, the best ranking signals are:

1. `HAS_CONCEPT_STATE.mastery_score`
2. `HAS_CONCEPT_STATE.struggle_score`
3. `PREREQUISITE_OF.strength`
4. `TESTS.weight`
5. `RECOMMENDED_FOR.weight`
6. `RELATED_TO.weight`

Simple intuition:

- student state says what the learner needs
- prerequisite strength says what blocks progression
- test weight says how strongly an exercise represents a concept
- recommended-for weight says how appropriate an exercise is for a path

## 7. Practical Defaults

If you want a simple stable first version, use:

- `PREREQUISITE_OF.strength` in `{1.0, 0.6, 0.3}`
- `TESTS.weight` in `{1.0, 0.7, 0.3}`
- `RELATED_TO.weight` in `{1.0, 0.7, 0.3}`
- `RECOMMENDED_FOR.weight` in `{1.0, 0.7, 0.3}`
- `mastery_score`, `struggle_score`, `confidence` in `0.0..1.0`

This gives enough precision for ranking without making the graph too hard to maintain.
