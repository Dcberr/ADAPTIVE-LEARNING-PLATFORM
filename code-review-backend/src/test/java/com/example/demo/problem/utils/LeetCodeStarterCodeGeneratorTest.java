package com.example.demo.problem.utils;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("LeetCodeStarterCodeGenerator Tests")
class LeetCodeStarterCodeGeneratorTest {

    private final LeetCodeStarterCodeGenerator generator = new LeetCodeStarterCodeGenerator();

    @Test
    @DisplayName("Should normalize raw C++ LeetCode starter code into executable template")
    void shouldNormalizeRawCppStarterCode() {
        String rawSnippet = """
                class Solution {
                public:
                    vector<int> twoSum(vector<int>& numbers, int target) {
                        
                    }
                };
                """;

        String template = generator.normalizeStarterCode("cpp", rawSnippet);

        assertTrue(template.contains("#include <vector>"));
        assertTrue(template.contains("//STUDENT_CODE_HERE"));
        assertTrue(template.contains("int main()"));
        assertTrue(template.contains("Solution solution;"));
    }

    @Test
    @DisplayName("Should avoid emitting unused C++ parse helpers for return-only types")
    void shouldAvoidUnusedCppParseHelpersForReturnOnlyTypes() {
        String rawSnippet = """
                class Solution {
                public:
                    vector<string> addOperators(string num, int target) {
                        
                    }
                };
                """;

        String template = generator.normalizeStarterCode("cpp", rawSnippet);

        assertTrue(template.contains("static string parseStringValue"));
        assertTrue(template.contains("static int parseInt"));
        assertTrue(template.contains("printVector(result);"));
        assertFalse(template.contains("static vector<string> parseVectorString"));
    }

    @Test
    @DisplayName("Should generate runnable C++ template for free function snippets")
    void shouldGenerateRunnableCppTemplateForFreeFunctionSnippets() {
        String rawSnippet = """
                string convertToTitle(int columnNumber) {
                }
                """;

        String template = generator.generateCppTemplatePublic(rawSnippet);

        assertTrue(template.contains("auto result = convertToTitle(columnNumber);"));
        assertFalse(template.contains("Solution solution;"));
    }

    @Test
    @DisplayName("Should print C++ string results as quoted JSON strings")
    void shouldPrintCppStringResultsAsQuotedJsonStrings() {
        String rawSnippet = """
                string convertToTitle(int columnNumber) {
                }
                """;

        String template = generator.generateCppTemplatePublic(rawSnippet);

        assertTrue(template.contains("static void printValue(const string& value)"));
        assertTrue(template.contains("escapeString(value)"));
        assertTrue(template.contains("printValue(result);"));
    }

    @Test
    @DisplayName("Should print C++ vector string results with quoted elements")
    void shouldPrintCppVectorStringResultsWithQuotedElements() {
        String rawSnippet = """
                class Solution {
                public:
                    vector<string> addOperators(string num, int target) {
                    }
                };
                """;

        String template = generator.generateCppTemplatePublic(rawSnippet);

        assertTrue(template.contains("printValue(values[i]);"));
    }

    @Test
    @DisplayName("Should normalize raw Java LeetCode starter code into executable template")
    void shouldNormalizeRawJavaStarterCode() {
        String rawSnippet = """
                class Solution {
                    public int[] twoSum(int[] nums, int target) {
                        
                    }
                }
                """;

        String template = generator.normalizeStarterCode("java", rawSnippet);

        assertTrue(template.contains("class Main"));
        assertTrue(template.contains("//STUDENT_CODE_HERE"));
        assertTrue(template.contains("Solution solution = new Solution();"));
        assertTrue(template.contains("printResult(result);"));
    }

    @Test
    @DisplayName("Should normalize starter code map and preserve normalized keys")
    void shouldNormalizeStarterCodeMap() {
        Map<String, String> templates = generator.normalizeStarterCodes(Map.of(
                "C++", "class Solution { public: int sum(int a, int b) { } };",
                "Python3", "class Solution:\n    def sum(self, a: int, b: int) -> int:\n        pass\n"
        ));

        assertTrue(templates.containsKey("cpp"));
        assertTrue(templates.containsKey("python"));
        assertTrue(templates.get("cpp").contains("int main()"));
        assertTrue(templates.get("python").contains("if __name__ == \"__main__\":"));
        assertFalse(templates.get("python").contains("        pass\nif __name__"));
    }

    @Test
    @DisplayName("Should generate LeetCode starter codes for supported topic tags")
    void shouldGenerateLeetCodeStarterCodesForSupportedTopics() {
        Map<String, String> templates = generator.generateLeetCodeStarterCodes(
                Map.of("C++", """
                        class Solution {
                        public:
                            int maxProfit(vector<int>& prices) {
                            }
                        };
                        """),
                List.of("array", "simulation")
        );

        assertTrue(templates.containsKey("cpp"));
        assertTrue(templates.get("cpp").contains("int main()"));
        assertTrue(templates.get("cpp").contains("//STUDENT_CODE_HERE"));
    }

    @Test
    @DisplayName("Should generate matrix LeetCode starter codes for supported topic tags")
    void shouldGenerateMatrixLeetCodeStarterCodesForSupportedTopics() {
        Map<String, String> templates = generator.generateLeetCodeStarterCodes(
                Map.of("cpp", """
                        class Solution {
                        public:
                            vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {
                            }
                        };
                        """),
                List.of("matrix")
        );

        assertTrue(templates.containsKey("cpp"));
        assertTrue(templates.get("cpp").contains("parseVectorIntMatrix"));
        assertTrue(templates.get("cpp").contains("printVector(result);"));
    }

    @Test
    @DisplayName("Should generate recursion LeetCode starter codes for tree signatures")
    void shouldGenerateRecursionLeetCodeStarterCodesForTreeSignatures() {
        Map<String, String> templates = generator.generateLeetCodeStarterCodes(
                Map.of("cpp", """
                        class Solution {
                        public:
                            int maxDepth(TreeNode* root) {
                            }
                        };
                        """),
                List.of("recursion")
        );

        assertTrue(templates.containsKey("cpp"));
        assertTrue(templates.get("cpp").contains("struct TreeNode"));
        assertTrue(templates.get("cpp").contains("parseTreeNode"));
        assertTrue(templates.get("cpp").contains("int main()"));
    }

    @Test
    @DisplayName("Should skip LeetCode starter code generation for unsupported topic tags")
    void shouldSkipLeetCodeStarterCodesForUnsupportedTopics() {
        Map<String, String> templates = generator.generateLeetCodeStarterCodes(
                Map.of("cpp", """
                        class Solution {
                        public:
                            vector<vector<int>> generateMatrix(int n) {
                            }
                        };
                        """),
                List.of("graph")
        );

        assertEquals(Map.of(), templates);
    }
}
