# Testcase API

## 1. Create Testcase

### Endpoint

POST /testcases

---

### Description

Create a new testcase for a problem

---

### Request Body

```json id="7v2c0y"
{
  "problemId": "uuid",
  "input": "1 2",
  "expectedOutput": "3",
  "isSample": true,
  "explanation": "1 + 2 = 3"
}
```

---

### Response

```json id="n9xv2k"
{
  "success": true,
  "data": {
    "id": "uuid",
    "input": "1 2",
    "expectedOutput": "3",
    "isSample": true
  }
}
```

---

## 2. Get Testcases by Problem

### Endpoint

GET /testcases/problem/{problemId}

---

### Description

Get testcases of a problem

---

### Response

```json id="w2s8kx"
{
  "success": true,
  "data": [
    {
      "input": "1 2",
      "expectedOutput": "3",
      "isSample": true
    }
  ]
}
```

---

## Authentication

* Required for creating testcase
* Optional for viewing (depends on system)

---

## ⚠️ Important Note

* Only **sample testcases** should be returned to client
* Hidden testcases must NOT be exposed
