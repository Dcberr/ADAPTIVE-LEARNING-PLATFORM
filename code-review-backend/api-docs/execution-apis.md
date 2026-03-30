# Execution API

## 1. Run & Judge Code

### Endpoint

POST /execution/judge

---

### Description

Execute user code against multiple testcases and return result

---

### Request Body

```json
{
  "language": "java",
  "sourceCode": "public class Main { ... }",
  "testcases": [
    {
      "input": "1 2",
      "expectedOutput": "3"
    },
    {
      "input": "2 3",
      "expectedOutput": "5"
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
    "results": [
      {
        "input": "1 2",
        "expected": "3",
        "actual": "3",
        "status": "PASSED"
      },
      {
        "input": "2 3",
        "expected": "5",
        "actual": "4",
        "status": "FAILED"
      }
    ],
    "overallStatus": "FAILED"
  }
}
```

---

### Status Values

| Status | Meaning                 |
| ------ | ----------------------- |
| PASSED | Output matches expected |
| FAILED | Output mismatch         |
| ERROR  | Runtime/compile error   |

---

### Supported Languages

* java
* python
* c++
  *(tùy system bạn)*

---

### Notes

* Code is executed in isolated environment (Jobe)
* Execution time & memory may be limited
* Order of testcases matters

---

## Authentication

* Required (if system protected)
