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
3. The API upserts each prerequisite concept from the request payload.
4. The API refreshes `PREREQUISITE_OF` relations for the provided prerequisite concepts.
5. The API returns the final stored concept payload.

## Request Schema

```json
{
  "name": "string",
  "description": "string",
  "difficulty": 1,
  "prerequisites": [
    {
      "concept_id": "string",
      "name": "string",
      "description": "string",
      "difficulty": 1
    }
  ]
}
```

## Request Field Notes

- `concept_id`: concept identifier in the path.
- `name`: display name of the concept.
- `description`: optional concept explanation.
- `difficulty`: integer difficulty level.
- `prerequisites`: prerequisite concepts that should point to this concept with `PREREQUISITE_OF`.
- each prerequisite item is also upserted as a concept node.

## Example Request

Path:
`PATCH /api/v1/knowledgegraph/concepts/33333333-3333-3333-3333-333333333333`

Body:

```json
{
  "name": "Input/Output",
  "description": "Read data from standard input and print the correct result to standard output.",
  "difficulty": 1,
  "prerequisites": [
    {
      "concept_id": "11111111-1111-1111-1111-111111111111",
      "name": "Variables",
      "description": "Store values in named variables and update them during program execution.",
      "difficulty": 1
    },
    {
      "concept_id": "22222222-2222-2222-2222-222222222222",
      "name": "Basic Arithmetic",
      "description": "Use arithmetic operators on numeric values.",
      "difficulty": 1
    }
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
- `(:Concept {prerequisite_id})` for each prerequisite object
- `(:Concept)-[:PREREQUISITE_OF]->(:Concept)` for each prerequisite concept

The repository replaces existing incoming prerequisite edges for the main concept so the graph matches the latest request.
