# Concept API

## Endpoint

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/concepts/{concept_id}`

This API upserts a concept node in Neo4j, evaluates prerequisite strength with the LLM, and refreshes its prerequisite relationships.

## Purpose

Use this API when:

- you want to create or update a concept in the curriculum graph
- you want to maintain prerequisite ordering between concepts
- you want recommendation and exercise mapping to use a stable concept id

## Flow

1. The client sends `concept_id` in the path and concept fields in the body.
2. The API upserts the `Concept` node in Neo4j.
3. The API checks that every `prerequisite_id` already exists in Neo4j.
4. If any related concept is missing, the API returns an error and does not write anything.
5. The API uses the LLM to evaluate `PREREQUISITE_OF.strength` between the main concept and each prerequisite.
6. The API refreshes `PREREQUISITE_OF` relations for the provided prerequisite concepts.
7. The API returns the final stored concept payload.

## Request Schema

```json
{
  "name": "string",
  "description": "string",
  "difficulty": 1,
  "prerequisite_ids": ["string"]
}
```

## Request Field Notes

- `concept_id`: concept identifier in the path.
- `name`: display name of the concept.
- `description`: optional concept explanation.
- `difficulty`: integer difficulty level.
- `prerequisite_ids`: concept ids that should point to this concept with `PREREQUISITE_OF`.
- every prerequisite concept must already exist in the graph or the API returns an error.

## Example Request

Path:
`PATCH /api/v1/knowledgegraph/concepts/33333333-3333-3333-3333-333333333333`

Body:

```json
{
  "name": "Input/Output",
  "description": "Read data from standard input and print the correct result to standard output.",
  "difficulty": 1,
  "prerequisite_ids": [
    "11111111-1111-1111-1111-111111111111",
    "22222222-2222-2222-2222-222222222222"
  ]
}
```

## Response Schema

```json
{
  "concept": {
    "concept_id": "string",
    "name": "string",
    "description": "string",
    "difficulty": 1
  }
}
```

## Graph Writes

This API creates or updates:

- `(:Concept {concept_id})`
- `(:Concept)-[:PREREQUISITE_OF {strength}]->(:Concept)` for each prerequisite concept

The repository replaces existing incoming prerequisite edges for the main concept so the graph matches the latest request.

The `strength` property is evaluated automatically by the LLM using the main concept and each prerequisite concept.
If any `prerequisite_id` does not already exist, the API returns an error instead of creating placeholder nodes.
