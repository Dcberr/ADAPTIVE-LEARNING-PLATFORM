"""Test script to verify improved parser"""
from app.parser.problem_parser import parse_problem
import json

# Sample HTML from LeetCode (simplified)
sample_html = """
<h2>Longest Palindromic Substring</h2>
<p>Given a string <code>s</code>, return the longest palindromic substring in <s>.</p>

<strong>Examples:</strong>
<pre>
Input: s = "babad"
Output: "bab"
Explanation: "aba" is also a valid answer.
</pre>

<pre>
Input: s = "cbbd"
Output: "bb"
</pre>

<strong>Constraints:</strong>
<ul>
<li>1 &lt;= s.length &lt;= 1000</li>
<li>s consist of only digits and English letters.</li>
</ul>
"""

parsed = parse_problem(sample_html)

print("=" * 60)
print("PARSED RESULT:")
print("=" * 60)

print("\n1. CONTENT:")
print(parsed["content"][:200] + "...")

print("\n2. CONSTRAINTS (as list):")
print(json.dumps(parsed["constraints"], indent=2))

print("\n3. EXAMPLES (as dict):")
print(json.dumps(parsed["examples"], indent=2))
