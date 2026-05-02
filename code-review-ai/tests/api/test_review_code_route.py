import os
import json
import unittest
from uuid import uuid4

import httpx


class ReviewCodeApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_review_code_endpoint(self):
        base_url = os.getenv("REVIEW_API_BASE_URL", "http://localhost:8000")
        timeout_seconds = float(os.getenv("REVIEW_API_TIMEOUT", "3000"))
        output_dir = os.path.join("tests", "api", "output")
        output_path = os.path.join(output_dir, "review_code_response.json")
        payload = {
            "assignment": {
                "content": (
                    "Given an array of integers nums and an integer target, return indices "
                    "of the two numbers such that they add up to target. You may assume "
                    "that each input has exactly one solution, and you may not use the same "
                    "element twice. You can return the answer in any order."
                ),
                "language": "C++",
            },
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
            "test_results": [
                {
                    "testcase_id": str(uuid4()),
                    "name": "example 1",
                    "input": "nums = [2,7,11,15], target = 9",
                    "expect": "[0,1]",
                    "actual": "[0,1]",
                },
                {
                    "testcase_id": str(uuid4()),
                    "name": "example 2",
                    "input": "nums = [3,2,4], target = 6",
                    "expect": "[1,2]",
                    "actual": "[1,2]",
                },
                {
                    "testcase_id": str(uuid4()),
                    "name": "example 3",
                    "input": "nums = [3,3], target = 6",
                    "expect": "[0,1]",
                    "actual": "[]",
                },
            ],
            "history": [
                {
                    "submission_id": str(uuid4()),
                    "code": (
                        "#include <vector>\n"
                        "using namespace std;\n"
                        "\n"
                        "class Solution {\n"
                        "public:\n"
                        "    vector<int> twoSum(vector<int>& nums, int target) {\n"
                        "        return {};\n"
                        "    }\n"
                        "};\n"
                    ),
                    "failed_test_case_ids": [str(uuid4())],
                    "passed_test_case_ids": [str(uuid4())],
                }
            ],
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(f"{base_url}/api/v1/review_code", json=payload)
            response.raise_for_status()
            response_json = response.json()

        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(response_json, output_file, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    unittest.main()
