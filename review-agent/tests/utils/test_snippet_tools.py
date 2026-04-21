import unittest

from app.utils.code_diff import build_changed_line_summary
from app.utils.snippet_tools import compress_text, extract_related_snippets


class SnippetToolsTests(unittest.TestCase):
    def test_extract_related_snippets_finds_context_around_anchor(self):
        snippets = extract_related_snippets(
            code="int x;\nif (x > 0) {\n    cout << \"positive\";\n}\nreturn 0;",
            anchors=["if (x > 0) {"],
        )

        self.assertTrue(snippets)
        self.assertIn('cout << "positive";', snippets[0])

    def test_build_changed_line_summary_returns_diff_like_lines(self):
        changes = build_changed_line_summary(
            previous_code='cout << "positive";',
            current_code='cout << "positive even";',
        )

        self.assertTrue(changes)
        self.assertTrue(any(line.startswith("- ") or line.startswith("+ ") for line in changes))

    def test_compress_text_truncates_long_text(self):
        self.assertTrue(compress_text("x" * 700, max_chars=50).endswith("..."))


if __name__ == "__main__":
    unittest.main()
