# Exercise Recommendation Rules

## Overview

This document defines the domain rules behind exercise graph authoring and recommendation-facing exercise relationships.

It focuses on:

- `Exercise -> Concept` coverage
- `Exercise -> Concept` recommendation-path fit
- `Exercise -> Exercise` relatedness
- which parts are client-provided ids versus LLM-evaluated relation properties

## Source Of Truth

For the exercise write flow:

- the `PUT /knowledgegraph/exercises/{exercise_id}` request provides:
  - exercise metadata
  - `concept_slugs`
- the `PATCH /knowledgegraph/exercises/{exercise_id}/relations` request provides:
  - `related_exercise_ids`
- Neo4j provides the related `Concept` and `Exercise` entities by id
- the knowledge-graph LLM evaluates relation weights and path metadata

The client does not send relation weights directly.

## Rule 1. `TESTS`

Relation:

- `(:Exercise)-[:TESTS {weight}]->(:Concept)`

Domain rule:

- every `concept_slug` in the exercise upsert request must already exist
- the API resolves the concept node from Neo4j before writing the relation
- `weight` is evaluated by the knowledge-graph LLM from:
  - main exercise title
  - description
  - content
  - resolved concept metadata

Meaning:

- `weight` measures how central the concept is to solving the exercise

## Rule 2. `RECOMMENDED_FOR`

Relation:

- `(:Exercise)-[:RECOMMENDED_FOR {path, weight}]->(:Concept)`

Domain rule:

- this relation is derived from the same resolved concept set as `TESTS`
- the client does not send `path` or `weight`
- the knowledge-graph LLM chooses:
  - `path`
  - `weight`

Allowed path values:

- `REINFORCE`
- `IMPROVE`
- `NEXT_CONCEPT`

Meaning:

- `path` tells recommendation why the exercise fits that concept
- `weight` tells recommendation how strong that fit is

## Rule 3. `RELATED_TO`

Relation:

- `(:Exercise)-[:RELATED_TO {weight, target_concept_id, shared_concept_ids, difficulty_gap, progression_score, similarity_score}]->(:Exercise)`

Domain rule:

- every `related_exercise_id` in the exercise relation patch request must already exist
- the API resolves the related exercise node from Neo4j before writing the relation
- the knowledge-graph LLM evaluates:
  - `weight`
  - `target_concept_id`
  - `shared_concept_ids`
  - `difficulty_gap`
  - `progression_score`
  - `similarity_score`

Meaning:

- `weight`: overall strength of the relation
- `target_concept_id`: concept that best explains the relation
- `shared_concept_ids`: concepts both exercises meaningfully share
- `difficulty_gap`: negative means easier, positive means harder
- `progression_score`: how good the target is as a next step
- `similarity_score`: how similar the target is to the source

## Validation Rule

If any related id is missing:

- missing `concept_id` -> exercise API returns `404`
- missing `related_exercise_id` -> exercise relation patch API returns `404`

The API does not create placeholder concept or exercise nodes from relation payloads.

## Recommendation Usage

Use these exercise-side relations in this order:

1. `RECOMMENDED_FOR.path`
2. `RECOMMENDED_FOR.weight`
3. `TESTS.weight`
4. `RELATED_TO.weight`
5. `RELATED_TO.progression_score`
6. `RELATED_TO.similarity_score`

Interpretation:

- `REINFORCE`: prefer high `RECOMMENDED_FOR.weight` and high `similarity_score`
- `IMPROVE`: prefer medium/high `progression_score` with moderate similarity
- `NEXT_CONCEPT`: prefer stronger `progression_score`, clearer `NEXT_STEP`, and a sensible positive `difficulty_gap`

## Maintenance Rule

If the exercise API changes any of these:

- request relation fields
- relation validation rules
- LLM-evaluated relation properties
- relation meaning

then this document must be updated together with:

- `docs/api/exercise-api.md`
- `docs/workflows/knowledge-graph-flow.md`
- `docs/architecture.md` when system behavior changes
