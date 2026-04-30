# Exercise API

## Endpoint

- Method: `PUT`
- Path: `/api/v1/knowledgegraph/exercises/{exercise_id}`

This API upserts an exercise node in Neo4j and refreshes its concept, recommendation-path, and related-exercise links.

## Purpose

Use this API when:

- you want to create or update an exercise in the curriculum graph
- you want to attach an exercise to the concepts it tests without manually choosing `TESTS.weight`
- you want recommendation flow to let the knowledge-graph LLM decide which `AssignedPath` values fit each concept
- you want exercise metadata and exercise-to-concept relations to be overwritten together from one request

## Flow

1. The client sends `exercise_id` in the path and exercise fields in the body.
2. The API upserts the `Exercise` node and its properties in Neo4j.
3. The API checks that every `concept_slug` already exists in Neo4j.
4. If any concept is missing, the API returns an error and does not write concept links.
5. The API scores `TESTS.weight` and chooses `RECOMMENDED_FOR.path` and `RECOMMENDED_FOR.weight`.
6. The repository clears previous `TESTS` and `RECOMMENDED_FOR` links owned by the main exercise.
7. The repository rebuilds weighted exercise-to-concept links from the evaluated result.
8. The API returns the stored exercise payload.

Exercise-to-exercise relations are updated separately through `PATCH /api/v1/knowledgegraph/exercises/{exercise_id}/relations`.

## Request Schema

```json
{
  "slug": "string",
  "title": "string",
  "description": "string",
  "content": "string",
  "difficulty": "string",
  "concept_slugs": ["string"]
}
```

## Request Field Notes

- `exercise_id`: exercise identifier in the path.
- `slug`: optional exercise slug.
- `title`: exercise title.
- `description`: short exercise summary.
- `content`: full exercise statement.
- `difficulty`: free-form difficulty label such as `easy`, `medium`, or `hard`.
- `concept_slugs`: existing concept slugs to attach to the main exercise through `TESTS`.
- every `concept_slug` must already exist in the graph or the API returns an error.

## Example Request

Path:
`PUT /api/v1/knowledgegraph/exercises/exercise-two-sum`

Body:

```json
{
  "slug": "two-sum",
  "title": "Two Sum",
  "description": "Read two integers and print their sum.",
  "content": "Write a program that reads two integers and prints their sum.",
  "difficulty": "easy",
  "concept_slugs": ["arrays", "addition"]
}
```

## Response Schema

```json
{
  "exercise": {
    "exercise_id": "string",
    "slug": "string",
    "title": "string",
    "description": "string",
    "content": "string",
    "difficulty": "string",
    "concept_slugs": ["string"]
  }
}
```

## Graph Writes

This API creates or updates:

- `(:Exercise {exercise_id})`
- exercise node properties such as `slug`, `title`, `description`, `content`, `difficulty`, and `concept_slugs`
- `(:Exercise)-[:TESTS {weight}]->(:Concept)` for each `concept_slugs[]` entry
- `(:Exercise)-[:RECOMMENDED_FOR {path, weight}]->(:Concept)` for each concept/path combination

Before rebuilding those links, the API validates that all concept slugs already exist. Then it evaluates `TESTS.weight` and `RECOMMENDED_FOR` metadata, overwrites the exercise fields, and clears existing `TESTS` and `RECOMMENDED_FOR` edges for the main exercise so the graph matches the request exactly.

## Exercise Relation Patch

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/exercises/{exercise_id}/relations`

Use this endpoint when you only want to overwrite outgoing `(:Exercise)-[:RELATED_TO]->(:Exercise)` relations for one exercise.
If `concept_slugs` is present, the API also adds those concept slugs onto the exercise node and refreshes the exercise-to-concept links from the merged set.

Request schema:

```json
{
  "concept_slugs": ["string"],
  "related_exercise_slugs": ["string"]
}
```
