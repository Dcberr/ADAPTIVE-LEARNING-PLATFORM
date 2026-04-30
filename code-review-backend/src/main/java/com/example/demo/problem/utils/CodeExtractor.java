package com.example.demo.problem.utils;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class CodeExtractor {

    private static final String FUNCTION_START_PATTERN = "{{FUNCTION_SIGNATURE}}";
    private static final String STUDENT_CODE_PLACEHOLDER = "//STUDENT_CODE_HERE";
    private static final Pattern BRACED_FUNCTION_PATTERN = Pattern.compile(
            "([a-zA-Z_][\\w:<>&*\\[\\],\\s]+)\\s+([a-zA-Z_][\\w]*)\\s*\\([^)]*\\)\\s*\\{"
    );
    private static final Pattern JS_FUNCTION_PATTERN = Pattern.compile(
            "(?:var|let|const)\\s+[A-Za-z_][\\w]*\\s*=\\s*function\\s*\\([^)]*\\)\\s*\\{|function\\s+[A-Za-z_][\\w]*\\s*\\([^)]*\\)\\s*\\{"
    );
    private static final Pattern PYTHON_FUNCTION_PATTERN = Pattern.compile(
            "(?m)^\\s*def\\s+[A-Za-z_][\\w]*\\s*\\([^)]*\\)\\s*(?:->\\s*[^:]+)?:\\s*$"
    );

    public static String extractFunctionSkeleton(String template) {
        if (template == null || template.isEmpty()) {
            return "";
        }

        try {
            int functionStart = template.indexOf(FUNCTION_START_PATTERN);
            if (functionStart != -1) {
                return extractByPlaceholder(template, functionStart);
            }

            String pythonSkeleton = extractPythonFunction(template);
            if (pythonSkeleton != null) {
                return pythonSkeleton;
            }

            String jsSkeleton = extractJavascriptFunction(template);
            if (jsSkeleton != null) {
                return jsSkeleton;
            }

            String bracedSkeleton = extractBracedFunction(template);
            if (bracedSkeleton != null) {
                return bracedSkeleton;
            }

            log.warn("No function found, returning full template");
            return template;
        } catch (Exception e) {
            log.error("Error extracting function skeleton", e);
            return template;
        }
    }

    private static String extractByPlaceholder(String template, int functionStart) {
        String afterFunction = template.substring(functionStart);
        int mainIndex = findMainIndex(afterFunction);
        String functionPart = (mainIndex == -1) ? afterFunction : afterFunction.substring(0, mainIndex);
        return functionPart.trim();
    }

    private static String extractBracedFunction(String template) {
        String normalized = template.replaceAll("(?m)^\\s*(public|private|protected)\\s*:\\s*$", "");
        Matcher matcher = BRACED_FUNCTION_PATTERN.matcher(normalized);
        if (!matcher.find()) {
            return null;
        }

        int start = matcher.start();
        int firstBrace = normalized.indexOf("{", start);
        int end = findMatchingBrace(normalized, firstBrace);
        if (end == -1) {
            return null;
        }

        return normalized.substring(start, end + 1).trim();
    }

    private static String extractJavascriptFunction(String template) {
        Matcher matcher = JS_FUNCTION_PATTERN.matcher(template);
        if (!matcher.find()) {
            return null;
        }

        int start = matcher.start();
        int firstBrace = template.indexOf("{", matcher.start());
        int end = findMatchingBrace(template, firstBrace);
        if (end == -1) {
            return null;
        }

        return template.substring(start, end + 1).trim();
    }

    private static String extractPythonFunction(String template) {
        Matcher matcher = PYTHON_FUNCTION_PATTERN.matcher(template);
        if (!matcher.find()) {
            return null;
        }

        int start = matcher.start();
        int bodyStart = matcher.end();
        int end = findPythonBlockEnd(template, bodyStart);
        return template.substring(start, end).trim();
    }

    private static int findMainIndex(String code) {
        String[] patterns = {
                "int main(",
                "void main(",
                "public static void main",
                "public static int main",
                "if __name__ == \"__main__\":",
                "const fs = require('fs')"
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

    public static String combineWithStudentCode(String template, String studentCode) {
        if (template == null || template.isEmpty()) {
            return studentCode;
        }

        if (studentCode == null || studentCode.isBlank()) {
            studentCode = defaultStudentCode(template);
        }

        studentCode = studentCode.trim();
        if (containsFunctionDefinition(studentCode)) {
            studentCode = extractBody(studentCode);
        }

        if (studentCode.contains("main(") || studentCode.contains("if __name__ == \"__main__\":")) {
            throw new RuntimeException("Do not define main function.");
        }

        String indentedCode = indentForTemplate(template, studentCode);
        return template.replace(STUDENT_CODE_PLACEHOLDER, indentedCode);
    }

    private static String defaultStudentCode(String template) {
        return template.contains("def ") ? "pass" : "// TODO: implement solution";
    }

    private static boolean containsFunctionDefinition(String code) {
        return BRACED_FUNCTION_PATTERN.matcher(code).find()
                || JS_FUNCTION_PATTERN.matcher(code).find()
                || PYTHON_FUNCTION_PATTERN.matcher(code).find();
    }

    private static String indentForTemplate(String template, String code) {
        int placeholderIndex = template.indexOf(STUDENT_CODE_PLACEHOLDER);
        if (placeholderIndex == -1) {
            return code;
        }

        int lineStart = template.lastIndexOf('\n', placeholderIndex);
        int start = lineStart == -1 ? 0 : lineStart + 1;
        int whitespaceCount = 0;
        while (start + whitespaceCount < template.length()
                && Character.isWhitespace(template.charAt(start + whitespaceCount))
                && template.charAt(start + whitespaceCount) != '\n') {
            whitespaceCount++;
        }

        String prefix = " ".repeat(whitespaceCount);
        return prefix + code.replace("\n", "\n" + prefix);
    }

    private static String extractBody(String code) {
        Matcher pythonMatcher = PYTHON_FUNCTION_PATTERN.matcher(code);
        if (pythonMatcher.find()) {
            int bodyStart = pythonMatcher.end();
            int bodyEnd = findPythonBlockEnd(code, bodyStart);
            String body = code.substring(bodyStart, bodyEnd).strip();
            return dedentPythonBlock(body);
        }

        int firstBrace = code.indexOf("{");
        int lastBrace = code.lastIndexOf("}");
        if (firstBrace == -1 || lastBrace == -1 || lastBrace <= firstBrace) {
            return code;
        }

        return code.substring(firstBrace + 1, lastBrace).trim();
    }

    private static String dedentPythonBlock(String block) {
        String[] lines = block.split("\n", -1);
        int minIndent = Integer.MAX_VALUE;
        for (String line : lines) {
            if (line.isBlank()) {
                continue;
            }
            int indent = 0;
            while (indent < line.length() && Character.isWhitespace(line.charAt(indent))) {
                indent++;
            }
            minIndent = Math.min(minIndent, indent);
        }

        if (minIndent == Integer.MAX_VALUE || minIndent == 0) {
            return block;
        }

        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i];
            if (line.isBlank()) {
                builder.append(line.stripTrailing());
            } else {
                builder.append(line.substring(Math.min(minIndent, line.length())));
            }
            if (i < lines.length - 1) {
                builder.append('\n');
            }
        }
        return builder.toString().trim();
    }

    public static String extractFunctionSignature(String template) {
        if (template == null || template.isEmpty()) {
            return "";
        }

        try {
            int functionStart = template.indexOf(FUNCTION_START_PATTERN);
            if (functionStart != -1) {
                int openBrace = template.indexOf("{", functionStart);
                if (openBrace == -1) {
                    return "";
                }
                return template.substring(functionStart, openBrace)
                        .replace(FUNCTION_START_PATTERN, "")
                        .trim();
            }

            String pythonSkeleton = extractPythonFunction(template);
            if (pythonSkeleton != null) {
                int lineEnd = pythonSkeleton.indexOf('\n');
                return lineEnd == -1 ? pythonSkeleton.trim() : pythonSkeleton.substring(0, lineEnd).trim();
            }

            String functionSkeleton = extractJavascriptFunction(template);
            if (functionSkeleton == null) {
                functionSkeleton = extractBracedFunction(template);
            }
            if (functionSkeleton == null) {
                return "";
            }

            int openBrace = functionSkeleton.indexOf("{");
            return openBrace == -1 ? functionSkeleton.trim() : functionSkeleton.substring(0, openBrace).trim();
        } catch (Exception e) {
            log.error("Error extracting function signature", e);
            return "";
        }
    }

    private static int findMatchingBrace(String code, int openBrace) {
        int braceCount = 0;
        for (int i = openBrace; i < code.length(); i++) {
            char current = code.charAt(i);
            if (current == '{') {
                braceCount++;
            } else if (current == '}') {
                braceCount--;
                if (braceCount == 0) {
                    return i;
                }
            }
        }
        return -1;
    }

    private static int findPythonBlockEnd(String code, int fromIndex) {
        String[] lines = code.substring(fromIndex).split("\n", -1);
        int offset = fromIndex;
        int blockIndent = Integer.MAX_VALUE;

        for (String line : lines) {
            String fullLine = line;
            int lineLengthWithBreak = fullLine.length() + 1;
            if (fullLine.isBlank()) {
                offset += lineLengthWithBreak;
                continue;
            }

            int indent = 0;
            while (indent < fullLine.length() && Character.isWhitespace(fullLine.charAt(indent))) {
                indent++;
            }

            if (blockIndent == Integer.MAX_VALUE) {
                blockIndent = indent;
                offset += lineLengthWithBreak;
                continue;
            }

            if (indent < blockIndent) {
                return offset;
            }

            offset += lineLengthWithBreak;
        }

        return code.length();
    }
}
