# Assignment API

## 1. Create Assignment

### Endpoint

POST /assignments

### Description

Create a new assignment with problem and testcases

### Request Body (JSON)

```json
{
  "topicId": "uuid",
  "title": "Assignment 1",
  "deadline": "2026-04-01T23:59:00Z",
  "difficulty": "EASY",
  "problem": {
    "description": "Solve X problem",
    "testcases": [
      {
        "input": "1 2",
        "expectedOutput": "3",
        "isSample": true,
        "explanation": "1 + 2 = 3"
      }
    ]
  }
}
```

### Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "uuid",
    "title": "Assignment 1"
  }
}
```

---

## 2. Get Assignments by Topic

### Endpoint

GET /assignments/topic/{topicId}

### Description

Get all assignments of a topic

### Path Params

| Param   | Type | Description |
| ------- | ---- | ----------- |
| topicId | UUID | Topic ID    |

### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Assignment 1"
    }
  ]
}
```
