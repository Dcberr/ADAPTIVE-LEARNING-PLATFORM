# Submission API

## 1. Submit Code

### Endpoint

POST /submissions

---

### Description

Submit code for a problem and trigger execution & judging

---

### Request Body

```json
{
  "problemId": "uuid",
  "language": "java",
  "sourceCode": "public class Main { ... }"
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "submission-id",
    "status": "PENDING"
  }
}
```

---

## 2. Get My Submissions

### Endpoint

GET /submissions/me

---

### Description

Get submission overview of current user

---

### Response

```json
{
  "success": true,
  "data": [
    {
      "submissionId": "uuid",
      "assignmentTitle": "Assignment 1",
      "problemTitle": "Sum Two Numbers",
      "score": 10,
      "status": "PASSED",
      "submittedAt": "2026-03-22T10:00:00Z"
    }
  ]
}
```

---

## 3. Get Submission Detail

### Endpoint

GET /submissions/{submissionId}

---

### Description

Get full detail of a submission including testcase results

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "sourceCode": "...",
    "language": "java",
    "results": [
      {
        "input": "1 2",
        "expected": "3",
        "actual": "3",
        "status": "PASSED"
      }
    ]
  }
}
```

---

## 4. Get Submissions by Problem

### Endpoint

GET /submissions/problem/{problemId}

---

### Description

Get all submissions of a specific problem

---

### Response

```json
{
  "success": true,
  "data": [
    {
      "submissionId": "uuid",
      "score": 8,
      "status": "FAILED"
    }
  ]
}
```

---

## Submission Status

| Status  | Meaning               |
| ------- | --------------------- |
| PENDING | Waiting for execution |
| RUNNING | Being executed        |
| PASSED  | All testcases passed  |
| FAILED  | Some testcases failed |
| ERROR   | Runtime/compile error |

---

## Authentication

* Required for all endpoints

---

## Notes

* Submission triggers execution and judging
* Results may take time depending on system load
