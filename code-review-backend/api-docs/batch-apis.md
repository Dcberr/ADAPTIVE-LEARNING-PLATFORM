# LeetCode Batch Import API

## Endpoint

```
POST /problems/leetcode/batch
Content-Type: application/json
```

---

## Description

This API is used to import a batch of LeetCode problems into the system.

* Supports inserting multiple problems in a single request
* Prevents duplicates using `(source, externalId)`
* Automatically links related problems via `similarQuestionIds`
* Returns the final state of all processed problems after import

---

## Request Body

```json
[
  {
    "externalId": "two-sum",
    "title": "Two Sum",
    "description": "Given an array of integers nums and an integer target...",
    "difficulty": "EASY",
    "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9",
    "starterCodes": {
      "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        //STUDENT_CODE_HERE\n    }\n}",
      "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        //STUDENT_CODE_HERE\n    }\n};"
    },
    "similarQuestionIds": [
      "3sum",
      "two-sum-ii"
    ],
    "testcases": [
      {
        "input": "[2,7,11,15]\n9",
        "expectedOutput": "[0,1]",
        "isHidden": false,
        "explanation": "nums[0] + nums[1] = 9"
      }
    ]
  }
]
```

---

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "8503639a-be6a-4d71-8f46-63d94a059aba",
      "externalId": "two-sum",
      "title": "Two Sum",
      "description": "...",
      "difficulty": "EASY",
      "problemConstraint": "...",
      "type": "LEETCODE",
      "functionSkeletons": {
        "java": "int[] twoSum(int[] nums, int target) { ... }",
        "cpp": "vector<int> twoSum(vector<int>& nums, int target) { ... }"
      },
      "testcases": [
        {
          "input": "[2,7,11,15]\n9",
          "expectedOutput": "[0,1]"
        }
      ],
      "similarQuestionIds": [
        "3sum",
        "two-sum-ii"
      ]
    }
  ],
  "timestamp": "2026-04-27T12:54:11.29296"
}
```

---

## Field Explanation

### externalId

* The LeetCode problem identifier (slug)
* Used to map with external systems
* Unique per `source`

---

### similarQuestionIds

* List of related problems (by externalId)
* Always returned as an array
* Never `null`

Example:

```json
"similarQuestionIds": []
```

---

### functionSkeletons

* Extracted from `starterCodes`
* Contains only the function to implement
* Does not include `main()` or boilerplate code

---

### testcases

* List of testcases stored in the database
* May be empty if not provided during import

---

## Behavior

### Insert vs Existing

| Case           | Behavior               |
| -------------- | ---------------------- |
| Not existing   | Insert                 |
| Already exists | Reuse (no duplication) |

---

### Similar Linking

* Processed after insertion (2-phase)
* Independent of request order
* Supports bidirectional linking

---

### Duplicate Protection

* Based on `(source, externalId)`
* Prevents duplicate entries

---

## Important Notes

* The API returns the **final state from the database**
* Includes:

  * Insert/update results
  * Similar problem linking
  * Loaded testcases
* Lists are **never returned as null**

---

## Recommended Usage

* Intended for batch jobs / crawler services
* Should not be publicly exposed without authentication
* Can be used for:

  * Periodic data synchronization
  * Building recommendation graphs


---

## Database Verification

```sql
SELECT * FROM problems WHERE source = 'LEETCODE';
```

```sql
SELECT * FROM problem_similar;
```

---
