"""Debug script to test parser with real HTML structure"""
from app.parser.problem_parser import parse_problem
import json

# This is the actual HTML structure from LeetCode API
# Notice that examples don't come in <pre> tags but in text with newlines
sample_html = """
Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example 1:

Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:

Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:

Input: nums = [3,3], target = 6
Output: [0,1]

Constraints:

2 <= nums.length <= 10^4
-10^9 <= nums[i] <= 10^9
-10^9 <= target <= 10^9
Only one valid answer exists.

Follow-up: Can you come up with an algorithm that is less than O(n^2) time complexity?
"""

print("=" * 80)
print("TESTING PARSER WITH REAL HTML STRUCTURE")
print("=" * 80)

parsed = parse_problem(sample_html)

print("\n1. EXAMPLES EXTRACTED:")
print(json.dumps(parsed["examples"], indent=2))

print("\n2. CONSTRAINTS EXTRACTED:")
print(json.dumps(parsed["constraints"], indent=2))

print("\n3. Problem: Examples are empty?", len(parsed["examples"]) == 0)
