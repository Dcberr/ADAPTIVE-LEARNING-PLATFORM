
---

# Postman Test – LeetCode Batch Import API

## Endpoint

```http
POST /problems/leetcode/batch
Content-Type: application/json
```

---

## Request Body (Full Test Dataset)

```json
[
  {
    "externalId": "two-sum",
    "title": "Two Sum",
    "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
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
      },
      {
        "input": "[3,2,4]\n6",
        "expectedOutput": "[1,2]",
        "isHidden": true,
        "explanation": ""
      }
    ]
  },
  {
    "externalId": "3sum",
    "title": "3Sum",
    "description": "Given an integer array nums, return all the triplets such that they add up to 0.",
    "difficulty": "MEDIUM",
    "constraints": "3 <= nums.length <= 3000\n-10^5 <= nums[i] <= 10^5",
    "starterCodes": {
      "java": "class Solution {\n    public List<List<Integer>> threeSum(int[] nums) {\n        //STUDENT_CODE_HERE\n    }\n}",
      "cpp": "class Solution {\npublic:\n    vector<vector<int>> threeSum(vector<int>& nums) {\n        //STUDENT_CODE_HERE\n    }\n};"
    },
    "similarQuestionIds": [
      "two-sum"
    ],
    "testcases": [
      {
        "input": "[-1,0,1,2,-1,-4]",
        "expectedOutput": "[[-1,-1,2],[-1,0,1]]",
        "isHidden": false,
        "explanation": ""
      }
    ]
  },
  {
    "externalId": "two-sum-ii",
    "title": "Two Sum II - Input Array Is Sorted",
    "description": "Given a sorted array, return indices of two numbers such that they add up to target.",
    "difficulty": "MEDIUM",
    "constraints": "2 <= numbers.length <= 3 * 10^4\n-1000 <= numbers[i] <= 1000",
    "starterCodes": {
      "java": "class Solution {\n    public int[] twoSum(int[] numbers, int target) {\n        //STUDENT_CODE_HERE\n    }\n}"
    },
    "similarQuestionIds": [
      "two-sum"
    ],
    "testcases": [
      {
        "input": "[2,7,11,15]\n9",
        "expectedOutput": "[1,2]",
        "isHidden": false,
        "explanation": "1-based index"
      }
    ]
  },
  {
    "externalId": "longest-substring-without-repeating-characters",
    "title": "Longest Substring Without Repeating Characters",
    "description": "Find the length of the longest substring without repeating characters.",
    "difficulty": "MEDIUM",
    "constraints": "0 <= s.length <= 5 * 10^4",
    "starterCodes": {
      "java": "int lengthOfLongestSubstring(String s) {\n    //STUDENT_CODE_HERE\n}"
    },
    "similarQuestionIds": [],
    "testcases": [
      {
        "input": "abcabcbb",
        "expectedOutput": "3",
        "isHidden": false,
        "explanation": ""
      },
      {
        "input": "bbbbb",
        "expectedOutput": "1",
        "isHidden": true,
        "explanation": ""
      }
    ]
  }
]
```

---

# Expected Result

```json
{
  "success": true,
  "data": "Imported successfully"
}
```

---

