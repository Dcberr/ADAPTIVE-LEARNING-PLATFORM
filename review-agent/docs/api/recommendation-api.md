# Recommendation API

## Endpoint

- Method: `POST`
- Path: `/api/v1/recommendation`

This API generates a roadmap of recommended next exercises for a student based on the current exercise and stored graph context.

## Purpose

Use this API when:

- you want the next exercise roadmap after a reviewed submission
- you want recommendation to use the latest review, recent review history, submission trend, and student profile
- you want graph-weighted exercise selection with student-facing explanation

## Flow

1. The client sends `student_id` and `exercise_id`.
2. The service loads the latest review, review history, submission trend, student profile, and current concept from Neo4j.
3. The service uses an internal planner LLM to choose a fixed query plan, start entity, target-concept hint, and path preference.
4. The service combines that planner decision with graph-backed rules to choose the assigned path and target concept.
5. The service ranks candidate exercises from weighted graph relations.
6. The service builds a roadmap of ordered exercises.
7. The LLM explains the selected roadmap and produces student-facing directives.
8. The service stores `ASSIGNED` and `RECOMMENDS` relations for the selected roadmap.
9. The API returns the roadmap response.

## Request Schema

```json
{
  "student_id": "string",
  "exercise_id": "string"
}
```

## Example Request

```json
{
  "student_id": "student-001",
  "exercise_id": "exercise-two-sum"
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
  "reasoning": "string",
  "roadmap_summary": "string",
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

## Graph Signals Used

- latest `Review`
- recent `NEXT_REVIEW_OF`
- latest `Submission`
- recent `NEXT_ATTEMPT`
- `Student` profile
- `Exercise -> TESTS -> Concept`
- `Exercise -> RECOMMENDED_FOR -> Concept`
- `Exercise -> RELATED_TO -> Exercise`
- `Concept -> PREREQUISITE_OF -> Concept`

## Notes

- recommendation uses an internal planner step, but graph-weighted relations still choose the final roadmap before the LLM writes explanations
- student profile is used as an adjustment layer, not as the primary selector
- `focus_concept_id` is the main concept the recommendation flow chose to emphasize
- each roadmap exercise also returns its own `concept_ids` from Neo4j node data
- the roadmap step no longer exposes `focus`, `path`, or `target_concept`
- each roadmap exercise carries `concept_ids` so the client can read concept coverage directly from Neo4j-backed exercise data
