# Student Profile Import API

## Endpoint

- Method: `PATCH`
- Path: `/api/v1/knowledgegraph/students/{student_id}`

This API inserts a student profile into the knowledge graph if the student does not already exist. If the student already exists, the current implementation returns the existing stored profile and does not update it.

## Purpose

Use this API when:

- you want to seed a student into Neo4j before recommendation runs
- you already have a profile score for the student

## Flow

1. The client sends `student_id` in the path and `student_profile` in the body.
2. The API checks whether the student already exists in Neo4j.
3. If the student does not exist, the repository creates the `Student` node and stores the profile scores.
4. If the student already exists, the repository leaves it unchanged.
5. The API returns `student_id` with the stored profile values.

## Request Schema

```json
{
  "student_profile": {
    "concept_mastery": 0.6,
    "implementation_consistency": 0.6,
    "debugging_independence": 0.6,
    "efficiency_awareness": 0.6,
    "concept_transfer": 0.6,
    "learning_velocity": 0.6,
    "notes": "string"
  }
}
```

## Request Field Notes

- `student_id`: unique student identifier in the path.
- `student_profile`: current scoring snapshot for the student.
- each score uses `0.0` to `1.0`, where `1.0` represents 100%

## Example Request

```json
{
  "student_profile": {
    "concept_mastery": 0.68,
    "implementation_consistency": 0.62,
    "debugging_independence": 0.45,
    "efficiency_awareness": 0.41,
    "concept_transfer": 0.58,
    "learning_velocity": 0.64,
    "notes": "The student is progressing steadily and can solve basic exercises with light support."
  }
}
```

## Response Schema

```json
{
  "student_id": "string",
  "student_profile": {
    "concept_mastery": 0.6,
    "implementation_consistency": 0.6,
    "debugging_independence": 0.6,
    "efficiency_awareness": 0.6,
    "concept_transfer": 0.6,
    "learning_velocity": 0.6,
    "notes": "string"
  }
}
```

## Graph Writes

When the student does not exist yet, this API creates:

- `Student`
- profile score properties on that `Student`

When the student already exists:

- no student properties are updated

## Notes

- This endpoint currently behaves as an insert-if-missing API, not a true update API.
- The response now returns only `student_id` and `student_profile`.
- Example path: `PATCH /api/v1/knowledgegraph/students/student-001`
- For profile recalculation after a review, use `PATCH /api/v1/knowledgegraph/students/{student_id}/profile`.
