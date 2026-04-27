import unittest

from code_review_ai.prompts.review.improvement import build_improvement_messages


class ImprovementPromptTests(unittest.TestCase):
    def test_improvement_prompt_mentions_structured_cpp_context_and_warning_scope(self):
        messages = build_improvement_messages(
            "[function_definition | lines 1-8]\n"
            "   1 | int main() {\n"
            "   2 |     int x;\n"
            "   3 |     cin >> x;\n"
            "   4 |     if (x > 0) {\n"
            "   5 |         cout << x;\n"
            "   6 |     }\n"
            "   7 | }\n\n"
            "Potential code-quality hotspots:\n"
            "- There are several output statements; check whether output formatting could be simplified."
        )

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]

        self.assertIn("structured C++ code context", system_prompt)
        self.assertIn("STRUCTURED C++ CODE CONTEXT:", user_prompt)
        self.assertIn("Warn about code structure only when it could realistically confuse the student", user_prompt)
        self.assertIn("Do NOT talk about hidden test cases", user_prompt)


if __name__ == "__main__":
    unittest.main()
