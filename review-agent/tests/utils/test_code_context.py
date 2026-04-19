import unittest

from app.utils.code_context import (
    build_improvement_code_context,
    build_logic_code_context,
)


class CodeContextTests(unittest.TestCase):
    def test_short_cpp_code_context_returns_full_numbered_code(self):
        context = build_logic_code_context(
            code='#include <iostream>\nint main() {\n    int x;\n    std::cin >> x;\n    std::cout << x + 1;\n}',
            failed_tests=[
                {"id": "tc-1", "input": "1", "expected": "2", "actual": "11"}
            ],
        )

        self.assertIn("Full C++ code with line numbers:", context)
        self.assertIn("1 | #include <iostream>", context)
        self.assertIn("4 |     std::cin >> x;", context)
        self.assertIn("5 |     std::cout << x + 1;", context)

    def test_long_cpp_code_context_prefers_structural_chunks(self):
        filler = "\n".join([f"value_{index} = {index}" for index in range(1, 85)])
        code = (
            "#include <iostream>\n"
            "int solve(int x) {\n"
            "    if (x > 0) {\n"
            "        return x + 1;\n"
            "    }\n"
            "    return x;\n"
            "}\n\n"
            f"{filler}\n"
            "int main() {\n"
            "    int x;\n"
            "    std::cin >> x;\n"
            "    std::cout << solve(x);\n"
            "}\n"
        )

        context = build_logic_code_context(
            code=code,
            failed_tests=[
                {"id": "tc-2", "input": "-1", "expected": "-2", "actual": "-1"}
            ],
        )

        self.assertNotIn("Full code with line numbers:", context)
        self.assertIn("[", context)
        self.assertIn("lines", context)
        self.assertIn("return x + 1;", context)
        self.assertIn("std::cout << solve(x);", context)

    def test_improvement_code_context_includes_hotspots(self):
        code = (
            "#include <iostream>\n"
            "using namespace std;\n"
            "int main() {\n"
            "    int x;\n"
            "    cin >> x;\n"
            "    if (x > 0) {\n"
            "        cout << x;\n"
            "        cout << x + 1;\n"
            "        cout << x + 2;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        )

        context = build_improvement_code_context(code=code)

        self.assertIn("Full C++ code with line numbers:", context)
        self.assertIn("Potential code-quality hotspots:", context)
        self.assertIn("output statements", context)


if __name__ == "__main__":
    unittest.main()
