# Review Code API

## Endpoint

- Method: `POST`
- Path: `/api/v1/review_code`

This API runs the full codereviewai workflow over a student submission and returns structured educational feedback.

## Purpose

Use this API when:

- you want to review a student submission with the active multi-agent review flow
- you want line-level issues, fix suggestions, and a scorecard in one response
- you want review links that compare the current issue with previous attempts

## Flow

1. The client submits assignment context, current code, failed testcase results, and an optional `history` array sorted by time descending.
2. The API converts the payload into `ReviewState` for the LangGraph workflow.
3. The review service runs the review agents in sequence:
   - `logic`
   - `fix_hint`
   - `review_link`
   - `improve`
   - `overview`
   - `scoring`
4. The API assembles the workflow result into `ReviewResponse`.
5. The API returns the structured review payload directly.

## Request Schema

```json
{
  "assignment": {
    "content": "string",
    "language": "string"
  },
  "code": "string",
  "test_results": [
    {
      "testcase_id": "uuid",
      "name": "string",
      "status": "fail",
      "input": "string",
      "expect": "string",
      "actual": "string"
    }
  ],
  "history": [
    {
      "submission_id": "uuid",
      "code": "string",
      "failed_test_case_ids": ["uuid"],
      "passed_test_case_ids": ["uuid"]
    }
  ]
}
```

## Request Field Notes

- `assignment.content`: the task statement or requirement text.
- `assignment.language`: language label such as `Python`, `C`, or `C++`.
- `code`: current submission code to review.
- `test_results`: sandbox/testcase outputs for this submission.
- `history`: prior submissions sorted newest first.
- `history[].failed_test_case_ids`: testcase ids that failed in that past attempt.
- `history[].passed_test_case_ids`: testcase ids that passed in that past attempt.
- review-link uses all matching history entries for one testcase, but treats the newest matching entry as the main comparison anchor.

## Example Request

```json
{
  "assignment": {
    "content": "Write a program that reads two integers and prints their sum.",
    "language": "C++"
  },
  "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    string a, b;\n    cin >> a >> b;\n    cout << a + b;\n    return 0;\n}",
  "test_results": [
    {
      "testcase_id": "11111111-1111-1111-1111-111111111111",
      "name": "simple integers",
      "status": "fail",
      "input": "2 3",
      "expect": "5",
      "actual": "23"
    },
    {
      "testcase_id": "22222222-2222-2222-2222-222222222222",
      "name": "zero case",
      "status": "pass",
      "input": "0 4",
      "expect": "4",
      "actual": "4"
    }
  ],
  "history": [
    {
      "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int a;\n    string b;\n    cin >> a >> b;\n    cout << a + b;\n    return 0;\n}",
      "failed_test_case_ids": [
        "11111111-1111-1111-1111-111111111111"
      ],
      "passed_test_case_ids": [
        "22222222-2222-2222-2222-222222222222"
      ]
    }
  ]
}
```

## Response Schema

```json
{
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
        "previous_submission_id": "string",
        "previous_code_snippets": ["string"],
        "comparison_mode": "persistent",
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
  }
}
```

## Notes

- `scorecard` remains on a `1..5` review scale.
- each `history` item must include `submission_id`.
- `review_link` is only present when the service finds the first earlier submission whose `failed_test_case_ids` contains the same testcase id.
- `comparison_mode` is typically `persistent` or `historical_match`.
- This API returns review output only. Graph persistence is handled by the separate knowledge-graph APIs.
