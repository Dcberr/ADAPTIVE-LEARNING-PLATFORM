import json
import os
import unittest
from uuid import uuid4

import httpx


class RecommendationApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_recommendation_endpoint(self):
        base_url = os.getenv("RECOMMENDATION_API_BASE_URL", "http://localhost:8000")
        timeout_seconds = float(os.getenv("RECOMMENDATION_API_TIMEOUT", "3000"))
        output_dir = os.path.join("tests", "api", "output")
        output_path = os.path.join(output_dir, "recommendation_response.json")
        review_output_path = os.path.join(output_dir, "review_code_response.json")

        with open(review_output_path, "r", encoding="utf-8") as review_output_file:
            review_response = json.load(review_output_file)

        payload = {
            "student_id": str(uuid4()),
            "exercise": {
                "exercise_id": "1696ef9f-5d5d-4d3d-81ae-6f61ff7ad012",
                "slug": "two-sum",
                "title": "Two Sum",
                "description": "Find two numbers in an array that add up to a target.",
                "content": (
                    "Given an array of integers nums and an integer target, return indices "
                    "of the two numbers such that they add up to target. You may assume "
                    "that each input has exactly one solution, and you may not use the same "
                    "element twice. You can return the answer in any order."
                ),
                "difficulty": "easy",
                "concept_slugs": ["arrays", "hash-map", "brute-force"],
            },
            "review": {
                "review_id": str(uuid4()),
                "summary": review_response["summary"],
                "detail": review_response["detail"],
                "review_items": review_response["review_items"],
            },
            "submission": {
                "submission_id": str(uuid4()),
                "code": (
                    "#include <vector>\n"
                    "using namespace std;\n"
                    "\n"
                    "class Solution {\n"
                    "public:\n"
                    "    vector<int> twoSum(vector<int>& nums, int target) {\n"
                    "        for (int i = 0; i < nums.size(); i++) {\n"
                    "            for (int j = i + 1; j < nums.size(); j++) {\n"
                    "                if (nums[i] == nums[j]) {\n"
                    "                    continue;\n"
                    "                }\n"
                    "                if (nums[i] + nums[j] == target) {\n"
                    "                    return {i, j};\n"
                    "                }\n"
                    "            }\n"
                    "        }\n"
                    "        return {};\n"
                    "    }\n"
                    "};\n"
                ),
                "testcases": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "expect": "[0,1]",
                        "output": "[0,1]",
                    },
                    {
                        "input": "nums = [3,2,4], target = 6",
                        "expect": "[1,2]",
                        "output": "[1,2]",
                    },
                    {
                        "input": "nums = [3,3], target = 6",
                        "expect": "[0,1]",
                        "output": "[]",
                    },
                ],
                "created_at": "2026-05-01T10:00:00Z",
            },
            "focus_concept_ids": ["array"],
            "attempted_exercise_ids": [],
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                f"{base_url}/api/v1/recommendation", json=payload
            )
            response.raise_for_status()
            response_json = response.json()

        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(response_json, output_file, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    unittest.main()
