# LeetCode Batch APIs

## Endpoints

```http
POST /problems/leetcode/batch
PUT /problems/leetcode/batch
Content-Type: application/json
```

---

## Description

These APIs are used by batch jobs or crawler services to sync LeetCode problems into the system.

* `POST /problems/leetcode/batch` imports problems and skips creating duplicates
* `PUT /problems/leetcode/batch` performs batch upsert
* Both APIs automatically link related problems via `similarQuestionIds`
* Both APIs return the final state of all processed problems

---

## Request Body

Both endpoints use the same request body:

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

* The LeetCode problem identifier
* Used to match existing records
* Unique per `(source, externalId)`

---

### similarQuestionIds

* List of related problems by `externalId`
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
* For `PUT`, old testcases are removed and replaced by the request payload
* May be empty if not provided

---

## Behavior

### POST /problems/leetcode/batch

| Case | Behavior |
| --- | --- |
| Not existing | Insert |
| Already exists | Reuse existing record, no duplicate insert |

---

### PUT /problems/leetcode/batch

| Case | Behavior |
| --- | --- |
| Not existing | Insert new problem |
| Already exists | Update existing problem |

For `PUT`:

* Problem fields such as `title`, `description`, `difficulty`, `constraints`, and `starterCodes` are overwritten
* Existing testcases are deleted and recreated from the request
* Existing `similarProblems` links are cleared and rebuilt from `similarQuestionIds`

---

### Similar Linking

* Processed after insert or update
* Independent of request order
* Supports bidirectional linking when related problems exist in the database

---

### Duplicate Protection

* Based on `(source, externalId)`
* Prevents duplicate problem entries

---

## Important Notes

* The APIs return the final state from the database
* Includes inserted or updated problem data
* Includes similar problem linking
* Includes loaded testcases
* Lists are never returned as `null`

---

## Recommended Usage

* Intended for batch jobs or crawler services
* Should not be publicly exposed without authentication
* Can be used for periodic synchronization from LeetCode
* `PUT` is recommended when the crawler should keep local data fully in sync

---

## Database Verification

```sql
SELECT * FROM problems WHERE source = 'LEETCODE';
```

```sql
SELECT * FROM problem_similar;
```

```sql
SELECT * FROM testcases;
```

---
