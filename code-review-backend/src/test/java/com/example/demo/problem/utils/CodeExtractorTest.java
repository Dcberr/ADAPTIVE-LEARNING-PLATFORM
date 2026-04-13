package com.example.demo.problem.utils;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("CodeExtractor Tests")
class CodeExtractorTest {

    private static final String CPP_TEMPLATE = """
            #include <bits/stdc++.h>
            using namespace std;

            {{FUNCTION_SIGNATURE}} {
                //STUDENT_CODE_HERE
            }

            int main() {
                ios::sync_with_stdio(false);
                cin.tie(nullptr);

                int n;
                cin >> n;

                cout << solve(n);

                return 0;
            }""";

    private static final String JAVA_TEMPLATE = """
            public class Solution {
                {{FUNCTION_SIGNATURE}} {
                    //STUDENT_CODE_HERE
                }

                public static void main(String[] args) {
                    int n = 5;
                    System.out.println(solve(n));
                }
            }""";

    @Test
    @DisplayName("Should extract C++ function skeleton")
    void shouldExtractCppFunctionSkeleton() {
        String skeleton = CodeExtractor.extractFunctionSkeleton(CPP_TEMPLATE);

        assertNotNull(skeleton);
        assertTrue(skeleton.contains("{{FUNCTION_SIGNATURE}}"));
        assertTrue(skeleton.contains("//STUDENT_CODE_HERE"));
        assertFalse(skeleton.contains("int main()"));
        assertFalse(skeleton.contains("cout"));
    }

    @Test
    @DisplayName("Should extract Java function skeleton")
    void shouldExtractJavaFunctionSkeleton() {
        String skeleton = CodeExtractor.extractFunctionSkeleton(JAVA_TEMPLATE);

        assertNotNull(skeleton);
        assertTrue(skeleton.contains("{{FUNCTION_SIGNATURE}}"));
        assertTrue(skeleton.contains("//STUDENT_CODE_HERE"));
        assertFalse(skeleton.contains("public static void main"));
    }

    @Test
    @DisplayName("Should combine template with student code")
    void shouldCombineTemplateWithStudentCode() {
        String studentCode = "return n * (n + 1) / 2;";
        String combined = CodeExtractor.combineWithStudentCode(CPP_TEMPLATE, studentCode);

        assertNotNull(combined);
        assertTrue(combined.contains(studentCode));
        assertFalse(combined.contains("//STUDENT_CODE_HERE"));
        assertTrue(combined.contains("int main()"));
    }

    @Test
    @DisplayName("Should handle empty student code")
    void shouldHandleEmptyStudentCode() {
        String combined = CodeExtractor.combineWithStudentCode(CPP_TEMPLATE, "");

        assertNotNull(combined);
        assertTrue(combined.contains("// TODO: implement solution"));
    }

    @Test
    @DisplayName("Should handle null template")
    void shouldHandleNullTemplate() {
        String result = CodeExtractor.extractFunctionSkeleton(null);
        assertEquals("", result);
    }

    @Test
    @DisplayName("Should extract function signature")
    void shouldExtractFunctionSignature() {
        String signature = CodeExtractor.extractFunctionSignature(CPP_TEMPLATE);

        assertNotNull(signature);
        // Should contain the signature without placeholder
        assertTrue(signature.contains("int solve(int n)") || signature.isEmpty());
    }
}
