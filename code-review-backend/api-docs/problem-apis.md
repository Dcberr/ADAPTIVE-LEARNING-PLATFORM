# Problem API

## 1. Create Problem

### Endpoint

POST /problems

---

### Description

Create a new coding problem with description and testcases

---

### Request Body

```json
{
  "assignmentId": "uuid",
  "description": "Given two integers, return their sum",
  "testcases": [
    {
      "input": "1 2",
      "expectedOutput": "3",
      "isSample": true,
      "explanation": "1 + 2 = 3"
    },
    {
      "input": "5 7",
      "expectedOutput": "12",
      "isSample": false
    }
  ]
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "description": "Given two integers..."
  }
}
```

---

## 2. Get Problem Detail

### Endpoint

GET /problems/{problemId}

---

### Description

Get full problem detail including sample testcases

---

### Response

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "description": "Given two integers...",
    "difficulty": "EASY",
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

---

## Authentication

* Required for creating problem
* Optional for viewing (tuỳ system)

---

## Notes

* Only sample testcases should be returned to client
* Hidden testcases are used for judging only
