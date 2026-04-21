package com.example.demo.problem.utils;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class CodeExtractor {

    private static final String FUNCTION_START_PATTERN = "{{FUNCTION_SIGNATURE}}";
    private static final String STUDENT_CODE_PLACEHOLDER = "//STUDENT_CODE_HERE";

    public static String extractFunctionSkeleton(String template) {
        if (template == null || template.isEmpty()) {
            return "";
        }

        try {
            // ===== CASE 1: TEMPLATE DYNAMIC =====
            int functionStart = template.indexOf(FUNCTION_START_PATTERN);
            if (functionStart != -1) {
                return extractByPlaceholder(template, functionStart);
            }

            // ===== CASE 2: TEMPLATE HARD-CODE =====
            return extractByFunctionPattern(template);

        } catch (Exception e) {
            log.error("Error extracting function skeleton", e);
            return template;
        }
    }

    // ===============================
    // CASE 1: {{FUNCTION_SIGNATURE}}
    // ===============================
    private static String extractByPlaceholder(String template, int functionStart) {

        String afterFunction = template.substring(functionStart);

        int mainIndex = findMainIndex(afterFunction);

        String functionPart = (mainIndex == -1)
                ? afterFunction
                : afterFunction.substring(0, mainIndex);

        return functionPart.trim();
    }

    // ===============================
    // CASE 2: int solve(...) fallback
    // ===============================
    private static final Pattern FUNCTION_PATTERN = Pattern.compile(
        "([a-zA-Z_][\\w:<>&*\\s]+)\\s+([a-zA-Z_][\\w]*)\\s*\\([^)]*\\)\\s*\\{"
    );
    private static String extractByFunctionPattern(String template) {

        template = template.replaceAll("(?m)^\\s*(public|private|protected)\\s*:\\s*$", "");

        Matcher matcher = FUNCTION_PATTERN.matcher(template);

        if (!matcher.find()) {
            log.warn("No function found, returning full template");
            return template;
        }

        int start = matcher.start();
        int firstBrace = template.indexOf("{", start);

        int braceCount = 1;
        int end = firstBrace;

        for (int i = firstBrace + 1; i < template.length(); i++) {
            char c = template.charAt(i);

            if (c == '{') braceCount++;
            if (c == '}') braceCount--;

            if (braceCount == 0) {
                end = i;
                break;
            }
        }

        return template.substring(start, end + 1).trim();
    }

    // ===============================
    // FIND MAIN FUNCTION
    // ===============================
    private static int findMainIndex(String code) {

        String[] patterns = {
                "int main(",
                "void main(",
                "public static void main",
                "public static int main"
        };

        int mainIndex = -1;

        for (String pattern : patterns) {
            int idx = code.indexOf(pattern);
            if (idx != -1 && (mainIndex == -1 || idx < mainIndex)) {
                mainIndex = idx;
            }
        }

        return mainIndex;
    }

    // ===============================
    // COMBINE TEMPLATE + STUDENT CODE
    // ===============================
    public static String combineWithStudentCode(String template, String studentCode) {

        if (template == null || template.isEmpty()) {
            return studentCode;
        }

        if (studentCode == null || studentCode.isBlank()) {
            studentCode = "// TODO: implement solution";
        }

        // ===== CLEAN INPUT =====
        studentCode = studentCode.trim();

        // ===== VALIDATE: CHỈ CHO PHÉP BODY =====
        if (containsFunctionDefinition(studentCode)) {
            studentCode = extractBody(studentCode);
        }

        if (studentCode.contains("main(")) {
            throw new RuntimeException("Do not define main function.");
        }

        // ===== FIX INDENT (optional nhưng nên có) =====
        studentCode = indent(studentCode, 4);

        return template.replace(STUDENT_CODE_PLACEHOLDER, studentCode);
    }

    private static boolean containsFunctionDefinition(String code) {

        // detect kiểu: int xxx(...), void xxx(...), auto xxx(...)
        return code.matches("(?s).*\\b(int|long|double|void|auto|vector<.*>)\\s+\\w+\\s*\\(.*\\)\\s*\\{.*");
    }

    private static String indent(String code, int spaces) {
        String prefix = " ".repeat(spaces);
        return prefix + code.replace("\n", "\n" + prefix);
    }

    private static String extractBody(String code) {

        int firstBrace = code.indexOf("{");
        int lastBrace = code.lastIndexOf("}");

        if (firstBrace == -1 || lastBrace == -1 || lastBrace <= firstBrace) {
            return code; // fallback
        }

        return code.substring(firstBrace + 1, lastBrace).trim();
    }

    // ===============================
    // EXTRACT FUNCTION SIGNATURE
    // ===============================
    public static String extractFunctionSignature(String template) {

        if (template == null || template.isEmpty()) {
            return "";
        }

        try {
            // CASE 1: dynamic
            int functionStart = template.indexOf(FUNCTION_START_PATTERN);
            if (functionStart != -1) {
                int openBrace = template.indexOf("{", functionStart);
                if (openBrace == -1) return "";

                return template.substring(functionStart, openBrace)
                        .replace(FUNCTION_START_PATTERN, "")
                        .trim();
            }

            // CASE 2: fallback
            String skeleton = extractByFunctionPattern(template);
            int openBrace = skeleton.indexOf("{");

            if (openBrace == -1) return skeleton;

            return skeleton.substring(0, openBrace).trim();

        } catch (Exception e) {
            log.error("Error extracting function signature", e);
            return "";
        }
    }
}
