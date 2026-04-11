# Exercise API

## Endpoint

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/exercises/{exercise_id}`

This API upserts an exercise node in Neo4j and refreshes its concept links and recommendation-path links.

## Purpose

Use this API when:

- you want to create or update an exercise in the curriculum graph
- you want to attach an exercise to the concepts it tests
- you want recommendation flow to know which paths this exercise supports

## Flow

1. The client sends `exercise_id` in the path and exercise fields in the body.
2. The API upserts the `Exercise` node in Neo4j.
3. The repository clears previous `TESTS` and `RECOMMENDED_FOR` links for that exercise.
4. The repository rebuilds concept and path links from the new payload.
5. The API returns the final stored exercise payload.

## Request Schema

```json
{
  "title": "string",
  "description": "string",
  "content": "string",
  "difficulty": "string",
  "tags": ["string"],
  "concept_ids": ["string"],
  "recommended_paths": ["REINFORCE", "IMPROVE", "NEXT_CONCEPT"]
}
```

## Request Field Notes

- `exercise_id`: exercise identifier in the path.
- `title`: exercise title.
- `description`: short exercise summary.
- `content`: full exercise statement.
- `difficulty`: free-form difficulty label such as `easy`, `medium`, or `hard`.
- `tags`: optional exercise tags.
- `concept_ids`: concepts tested by this exercise.
- `recommended_paths`: allowed recommendation paths to attach between this exercise and its concepts.

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
  "concept_ids": ["variables", "input-output", "arithmetic"],
  "recommended_paths": ["REINFORCE", "IMPROVE"]
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
- `(:Exercise)-[:TESTS {weight: 1.0}]->(:Concept)` for each `concept_ids` entry
- `(:Exercise)-[:RECOMMENDED_FOR {path}]->(:Concept)` for each concept/path combination

Before rebuilding those links, the repository clears existing `TESTS` and `RECOMMENDED_FOR` edges for the exercise.
