# Exercise API

## Endpoint

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/exercises/{exercise_id}`

This API upserts an exercise node in Neo4j and refreshes its concept, recommendation-path, and related-exercise links.

## Purpose

Use this API when:

- you want to create or update an exercise in the curriculum graph
- you want to attach an exercise to the concepts it tests without manually choosing `TESTS.weight`
- you want recommendation flow to let the knowledge-graph LLM decide which `AssignedPath` values fit each concept
- you want to connect a main exercise to related exercises without manually choosing `RELATED_TO.weight`

## Flow

1. The client sends `exercise_id` in the path and exercise fields in the body.
2. The API upserts the `Exercise` node in Neo4j.
3. The API checks that every `concept_id` and `related_exercise_id` already exists in Neo4j.
4. If any related entity is missing, the API returns an error and does not write anything.
5. The API asks the knowledge-graph LLM evaluator to score `TESTS.weight`, choose `RECOMMENDED_FOR.path`, choose `RECOMMENDED_FOR.weight`, and evaluate `RELATED_TO` metadata such as weight, relation type, shared concepts, and progression similarity.
6. The repository clears previous `TESTS`, `RECOMMENDED_FOR`, and `RELATED_TO` links owned by the main exercise.
7. The repository rebuilds weighted concept, path, and related-exercise links from the evaluated result.
8. The API returns the final stored exercise payload.

## Request Schema

```json
{
  "title": "string",
  "description": "string",
  "content": "string",
  "difficulty": "string",
  "tags": ["string"],
  "concept_ids": ["string"],
  "related_exercise_ids": ["string"]
}
```

## Request Field Notes

- `exercise_id`: exercise identifier in the path.
- `title`: exercise title.
- `description`: short exercise summary.
- `content`: full exercise statement.
- `difficulty`: free-form difficulty label such as `easy`, `medium`, or `hard`.
- `tags`: optional exercise tags.
- `concept_ids`: existing concept ids to attach to the main exercise through `TESTS`.
- `related_exercise_ids`: existing exercise ids to attach to the main exercise through `RELATED_TO`.
- every `concept_id` and `related_exercise_id` must already exist in the graph or the API returns an error.

## Example Request

Path:
`PATCH /api/v1/knowledgegraph/exercises/exercise-two-sum`

Body:

```json
{
  "title": "Two Sum",
  "description": "Read two integers and print their sum.",
  "content": "Write a program that reads two integers and prints their sum.",
  "difficulty": "easy",
  "tags": ["math", "input-output"],
  "concept_ids": [
    "11111111-1111-1111-1111-111111111111",
    "33333333-3333-3333-3333-333333333333"
  ],
  "related_exercise_ids": [
    "exercise-sum-three-numbers"
  ]
}
```

## Response Schema

```json
{
  "exercise": {
    "exercise_id": "string",
    "title": "string",
    "description": "string",
    "content": "string",
    "difficulty": "string",
    "tags": ["string"]
  }
}
```

## Graph Writes

This API creates or updates:

- `(:Exercise {exercise_id})`
- `(:Exercise)-[:TESTS {weight}]->(:Concept)` for each `concept_ids[]` entry
- `(:Exercise)-[:RECOMMENDED_FOR {path, weight}]->(:Concept)` for each concept/path combination
- `(:Exercise)-[:RELATED_TO {weight, relation_type, target_concept_id, shared_concept_ids, difficulty_gap, progression_score, similarity_score}]->(:Exercise)` for each `related_exercise_ids[]` entry

Before rebuilding those links, the API validates that all related concept and exercise ids already exist. Then it evaluates `TESTS.weight`, `RECOMMENDED_FOR.path`, `RECOMMENDED_FOR.weight`, and `RELATED_TO` metadata with the knowledge-graph LLM, and finally the repository clears existing `TESTS`, `RECOMMENDED_FOR`, and outgoing `RELATED_TO` edges for the main exercise.
