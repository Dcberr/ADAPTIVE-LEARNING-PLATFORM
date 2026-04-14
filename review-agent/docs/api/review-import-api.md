# Review Import APIs

## Overview

The old combined `POST /api/v1/knowledgegraph/import-review` flow has been replaced by two separate full upsert APIs:

- `PUT /api/v1/knowledgegraph/submissions/{submission_id}`
- `PUT /api/v1/knowledgegraph/reviews/{review_id}`

These APIs are designed to be called in order:

1. upsert the submission
2. upsert the review for that submission

This split keeps graph validation explicit: the submission write confirms `Student` and `Exercise` exist first, and the review write confirms `Submission` exists before linking review data.

## Submission API

- Method: `PUT`
- Path: `/api/v1/knowledgegraph/submissions/{submission_id}`

### Validation Rules

- `student_id` must already exist in the graph
- `exercise_id` must already exist in the graph
- if either one does not exist, the API returns `404`

### Flow

1. The client sends `submission_id` in the path.
2. The API verifies that `student_id` and `exercise_id` already exist in Neo4j.
3. The repository inserts or updates the `Submission` node.
4. The repository refreshes `SUBMITTED` and `FOR_EXERCISE` relations to match the latest payload.
5. The repository refreshes `NEXT_ATTEMPT` relations around the submission for the same student and exercise, including progress scores between adjacent attempts.
6. The API returns the stored submission payload.

### Request Schema

```json
{
  "student_id": "string",
  "exercise_id": "string",
  "code": "string",
  "testcase_outputs": [
    {
      "expect": "string",
      "output": "string"
    }
  ]
}
```

### Example Request

Path:
`PUT /api/v1/knowledgegraph/submissions/submission-001`

Body:

```json
{
  "student_id": "student-001",
  "exercise_id": "exercise-two-sum",
  "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    string a, b;\n    cin >> a >> b;\n    cout << a + b;\n    return 0;\n}",
  "testcase_outputs": [
    {
      "expect": "5",
      "output": "23"
    },
    {
      "expect": "4",
      "output": "4"
    }
  ]
}
```

### Response Schema

```json
{
  "submission": {
    "submission_id": "string",
    "student_id": "string",
    "exercise_id": "string",
    "code": "string",
    "testcase_outputs": [
      {
        "expect": "string",
        "output": "string"
      }
    ],
    "created_at": "string"
  }
}
```

### Relations Updated

- `(:Student)-[:SUBMITTED]->(:Submission)`
- `(:Submission)-[:FOR_EXERCISE]->(:Exercise)`
- `(:Submission)-[:NEXT_ATTEMPT {student_id, linked_at, same_exercise, improvement_ratio, regression_ratio}]->(:Submission)` when there is a prior attempt by the same student on the same exercise

If the submission already exists, its stored fields are overwritten by the request and these relations are refreshed to match the latest `student_id`, `exercise_id`, and adjacent-attempt progression links.

## Review API

- Method: `PUT`
- Path: `/api/v1/knowledgegraph/reviews/{review_id}`

### Validation Rules

- `submission_id` must already exist in the graph
- if it does not exist, the API returns `404`
- `student_id` and `exercise_id` are derived from the linked submission
- all review fields in the request body are required
- the request overwrites the stored review fields for that `review_id`

### Flow

1. The client sends `review_id` in the path.
2. The API verifies that the referenced `submission_id` already exists.
3. The repository inserts or updates the `Review` node.
4. The repository derives `student_id` and `exercise_id` from the linked submission.
5. The repository refreshes review relations, including student, submission, exercise, and adjacent review-history links.
6. The API returns the stored review payload.

### Request Schema

```json
{
  "submission_id": "string",
  "summary": "string",
  "detail": "string",
  "review_items": [
    {
      "line": {
        "start": 1,
        "end": 1
      },
      "column": {
        "start": 1,
        "end": 10
      },
      "code_snippet": "string",
      "type": "Error",
      "issue": "string",
      "fix_suggestion": "string",
      "review_link": {
        "current_issue": "string",
        "current_code_snippet": "string",
        "previous_submission_indexes": [0],
        "previous_code_snippet": "string",
        "what_improved": "string",
        "what_still_needs_work": "string",
        "relation_summary": "string"
      }
    }
  ],
  "scorecard": {
    "problem_solving_creativity": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "logic_traceability": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "generalization_score": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "construct_appropriateness": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "self_correction_path": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "variable_understanding": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "control_flow_understanding": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "input_output_awareness": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "edge_case_awareness": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    },
    "debugging_readiness": {
      "score": 3,
      "label": "Developing",
      "explanation": "string"
    }
  },
  "current_concept": "string"
}
```

### Example Request

Path:
`PUT /api/v1/knowledgegraph/reviews/review-001`

Body:

```json
{
  "submission_id": "submission-001",
  "summary": "The submission reads values correctly but still treats them as strings.",
  "detail": "The student improved input handling compared with a previous attempt, but the arithmetic bug remains.",
  "review_items": [
    {
      "line": {
        "start": 4,
        "end": 4
      },
      "column": {
        "start": 13,
        "end": 18
      },
      "code_snippet": "cout << a + b;",
      "type": "Error",
      "issue": "The values are stored as strings, so `a + b` concatenates them instead of adding the numbers.",
      "fix_suggestion": "Read both values as integers or convert them before performing the addition."
    }
  ],
  "scorecard": {
    "problem_solving_creativity": {
      "score": 3,
      "label": "Developing",
      "explanation": "The student attempted a direct solution but missed the data type requirement."
    },
    "logic_traceability": {
      "score": 2,
      "label": "Needs Support",
      "explanation": "The output behavior does not align with the intended numeric logic."
    },
    "generalization_score": {
      "score": 2,
      "label": "Needs Support",
      "explanation": "The current solution does not reliably handle general numeric input."
    },
    "construct_appropriateness": {
      "score": 2,
      "label": "Needs Support",
      "explanation": "String variables are not appropriate for this arithmetic task."
    },
    "self_correction_path": {
      "score": 3,
      "label": "Developing",
      "explanation": "There is some progress from the prior attempt, but the key bug remains."
    },
    "variable_understanding": {
      "score": 2,
      "label": "Needs Support",
      "explanation": "The student has not yet chosen a numeric type for numeric data."
    },
    "control_flow_understanding": {
      "score": 3,
      "label": "Developing",
      "explanation": "The control flow is simple and mostly correct for the task."
    },
    "input_output_awareness": {
      "score": 3,
      "label": "Developing",
      "explanation": "The student understands basic input and output structure."
    },
    "edge_case_awareness": {
      "score": 2,
      "label": "Needs Support",
      "explanation": "The solution does not account for numeric correctness across all valid inputs."
    },
    "debugging_readiness": {
      "score": 3,
      "label": "Developing",
      "explanation": "The student shows some progress but still needs help identifying type-related bugs."
    }
  },
  "current_concept": "input-output"
}
```

### Response Schema

```json
{
  "review": {
    "review_id": "string",
    "student_id": "string",
    "exercise_id": "string",
    "submission_id": "string",
    "current_concept": "string",
    "created_at": "string",
    "summary": "string",
    "detail": "string"
  }
}
```

### Relations Updated

- `(:Student)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Submission)-[:RECEIVED_REVIEW]->(:Review)`
- `(:Review)-[:REVIEWS_SUBMISSION]->(:Submission)`
- `(:Review)-[:REVIEWS_EXERCISE]->(:Exercise)` when the submission is linked to an exercise
- `(:Review)-[:NEXT_REVIEW_OF {student_id, linked_at, same_concept, improvement_signal, severity_change}]->(:Review)` for adjacent reviews by the same student

If the review already exists, its properties are updated and these relations are refreshed to match the linked submission.
