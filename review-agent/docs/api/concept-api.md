# Concept API

## Endpoint

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/concepts/{concept_id}`

This API upserts a concept node in Neo4j and refreshes its prerequisite relationships.

## Purpose

Use this API when:

- you want to create or update a concept in the curriculum graph
- you want to maintain prerequisite ordering between concepts
- you want recommendation and exercise mapping to use a stable concept id

## Flow

1. The client sends `concept_id` in the path and concept fields in the body.
2. The API upserts the `Concept` node in Neo4j.
3. The API creates prerequisite concept placeholders when needed.
4. The API refreshes `PREREQUISITE_OF` relations for the provided prerequisite ids.
5. The API returns the final stored concept payload.

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

## Example Request

Path:
`PATCH /api/v1/knowledgegraph/concepts/input-output`

Body:

```json
{
  "name": "Input/Output",
  "description": "Read data from standard input and print the correct result to standard output.",
  "difficulty": 1,
  "prerequisite_ids": ["variables"]
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
- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)` for each prerequisite id

If a prerequisite concept does not already exist, the repository creates a placeholder concept node for it.
