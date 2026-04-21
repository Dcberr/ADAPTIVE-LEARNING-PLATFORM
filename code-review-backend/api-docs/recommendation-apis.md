# Recommendation API

## 1. Get Learning Recommendation

### Endpoint

POST /recommendations

---

### Description

Backend receives `student_id` and `current_exercise_id`, calls the recommend service at `http://review-agent:8000/api/v1/recommend`, then returns the service response to FE.

---

### Request Body

```json
{
  "student_id": "11111111-1111-1111-1111-111111111111",
  "current_exercise_id": "22222222-2222-2222-2222-222222222222"
}
```

---

### Success Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "student_id": "11111111-1111-1111-1111-111111111111",
    "current_exercise_id": "22222222-2222-2222-2222-222222222222",
    "anchor_concept": "two-pointers",
    "assigned_path": "IMPROVE",
    "focus_concept_id": "concept-01",
    "critical_errors": 1,
    "framework": {
      "risk_level": "medium",
      "readiness_level": "developing",
      "explanation": "Student is improving but still has one key gap."
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
      "content": "Student often misses boundary checks {ref_1}",
      "refs": [
        {
          "ref_id": "ref_1",
          "content": "Previous review detected index-out-of-range risk.",
          "ref_category": "code"
        }
      ]
    },
    "roadmap_summary": {
      "content": "Next best exercise is {ref_2}",
      "refs": [
        {
          "ref_id": "ref_2",
          "content": "Container With Most Water",
          "ref_category": "exercise"
        }
      ]
    },
    "roadmap": [
      {
        "step": 1,
        "exercise": {
          "exercise_id": "exercise-01",
          "title": "Container With Most Water",
          "description": "Practice two-pointer optimization",
          "content": "Find the max area...",
          "difficulty": "MEDIUM",
          "tags": ["array", "two-pointers"],
          "concept_ids": ["concept-01"],
          "directive": "Focus on pointer movement reasoning"
        }
      }
    ]
  },
  "timestamp": "2026-04-22T10:00:00"
}
```

---

### Authorization Rules

- Student can request recommendation for themself.
- Instructor/Admin can request recommendation for any student.

---

### Validation

- `student_id` must exist in `users`.
- `current_exercise_id` must exist in `problems`.

---

### Error Cases

- `404 User not found`
- `404 Problem not found`
- `403 Forbidden`
- `502 Recommendation service error`
