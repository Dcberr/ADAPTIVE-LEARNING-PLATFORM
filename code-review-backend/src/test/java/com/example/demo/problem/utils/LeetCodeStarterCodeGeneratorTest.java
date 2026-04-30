package com.example.demo.problem.utils;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

        assertTrue(template.contains("#include <bits/stdc++.h>"));
        assertTrue(template.contains("//STUDENT_CODE_HERE"));
        assertTrue(template.contains("int main()"));
        assertTrue(template.contains("Solution solution;"));
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
}
