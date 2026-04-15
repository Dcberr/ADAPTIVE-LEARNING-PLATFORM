# Recommendation API

## Endpoint

- Method: `POST`
- Path: `/api/v1/recommendation`

This API generates a roadmap of recommended next exercises for a student based on the current exercise and stored graph context.

## Purpose

Use this API when:

- you want the next exercise roadmap after a reviewed submission
- you want recommendation to use stored review, submission, profile, and graph context from Neo4j
- you want the roadmap explanation to cite previous review, code, and exercise evidence through structured refs

## Flow

1. The client sends `student_id` and `exercise_id`.
2. The service loads base context from Neo4j.
3. The LLM decides which extra context blocks should be loaded.
4. The service conditionally loads those extra context blocks.
5. The LLM decides the recommendation path and focus concept.
6. The service queries weighted candidate exercises from Neo4j.
7. The LLM selects the roadmap exercises and step directives.
8. The LLM builds structured explanation blocks with refs.
9. The service stores `ASSIGNED` and `RECOMMENDS` relations for the selected roadmap.
10. The API returns the roadmap response.

## Request Schema

```json
{
  "student_id": "string",
  "exercise_id": "string"
}
```

## Response Schema

```json
{
  "student_id": "string",
  "current_exercise_id": "string",
  "anchor_concept": "string",
  "assigned_path": "IMPROVE",
  "focus_concept_id": "string",
  "critical_errors": 1,
  "framework": {
    "risk_level": "medium",
    "readiness_level": "developing",
    "explanation": "string"
  },
  "graph_summary": {
    "current_concept_weight": 1.0,
    "best_path_weight": 0.91,
    "best_related_exercise_weight": 0.86,
    "latest_review_improvement_signal": 0.42,
    "latest_review_severity_change": -0.25,
    "latest_submission_improvement_ratio": 0.35,
    "latest_submission_regression_ratio": 0.0
  },
  "reasoning": {
    "content": "string with {ref_id}",
    "refs": [
      {
        "ref_id": "string",
        "content": "string",
        "ref_category": "code"
      }
    ]
  },
  "roadmap_summary": {
    "content": "string with {ref_id}",
    "refs": [
      {
        "ref_id": "string",
        "content": "string",
        "ref_category": "exercise"
      }
    ]
  },
  "roadmap": [
    {
      "step": 1,
      "exercise": {
        "exercise_id": "string",
        "title": "string",
        "description": "string",
        "content": "string",
        "difficulty": "string",
        "tags": ["string"],
        "concept_ids": ["string"],
        "directive": "string"
      }
    }
  ]
}
```

## Notes

- the recommendation flow is now LLM-led at four stages: context planning, path decision, roadmap selection, and explanation building
- graph retrieval still stays constrained to fixed repository queries; the LLM does not generate raw Cypher
- `focus_concept_id` is the concept the chosen roadmap is centered on
- explanation refs are always returned separately from the prose
- each explanation ref includes `ref_id`, `content`, and `ref_category`
- allowed `ref_category` values are `code`, `review`, and `exercise`
