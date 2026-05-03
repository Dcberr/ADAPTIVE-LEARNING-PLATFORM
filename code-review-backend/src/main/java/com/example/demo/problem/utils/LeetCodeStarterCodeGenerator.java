package com.example.demo.problem.utils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.stereotype.Component;

@Component
public class LeetCodeStarterCodeGenerator {

    private static final String STUDENT_CODE_PLACEHOLDER = "//STUDENT_CODE_HERE";
    private static final Pattern CPP_SOLUTION_CLASS_PATTERN = Pattern.compile("\\bclass\\s+Solution\\b");
        private static final String CPP_DEFAULT_INCLUDES = """
                        #include <algorithm>
                        #include <cctype>
                        #include <cmath>
                        #include <deque>
                        #include <functional>
                        #include <iomanip>
                        #include <iostream>
                        #include <limits>
                        #include <map>
                        #include <numeric>
                        #include <queue>
                        #include <set>
                        #include <sstream>
                        #include <stack>
                        #include <string>
                        #include <unordered_map>
                        #include <unordered_set>
                        #include <utility>
                        #include <vector>
                        """;





    private static final Pattern CPP_METHOD_PATTERN = Pattern.compile(
            "([a-zA-Z_][\\w:<>,\\s&*]*?)\\s+([a-zA-Z_][\\w]*)\\s*\\(([^)]*)\\)\\s*\\{"
    );
    private static final Pattern JAVA_METHOD_PATTERN = Pattern.compile(
            "((?:public|private|protected)\\s+)?(?:static\\s+)?([A-Za-z_][\\w<>,\\[\\]\\s?]*)\\s+([A-Za-z_][\\w]*)\\s*\\(([^)]*)\\)\\s*\\{"
    );
    private static final Pattern JS_FUNCTION_PATTERN = Pattern.compile(
            "(?:var|let|const)\\s+([A-Za-z_][\\w]*)\\s*=\\s*function\\s*\\(([^)]*)\\)\\s*\\{|function\\s+([A-Za-z_][\\w]*)\\s*\\(([^)]*)\\)\\s*\\{"
    );
    private static final Pattern PYTHON_METHOD_PATTERN = Pattern.compile(
            "(?m)^\\s*def\\s+([A-Za-z_][\\w]*)\\s*\\(([^)]*)\\)\\s*(?:->\\s*([^:]+))?:\\s*$"
    );

    public Map<String, String> generateStarterCodes(String leetCodeLanguage, String leetCodeCodeSnippet) {
        if (leetCodeCodeSnippet == null || leetCodeCodeSnippet.isBlank()) {
            return Collections.emptyMap();
        }

        String normalizedLanguage = normalizeLanguage(leetCodeLanguage);
        return Map.of(normalizedLanguage, normalizeStarterCode(normalizedLanguage, leetCodeCodeSnippet));
    }

    public Map<String, String> normalizeStarterCodes(Map<String, String> starterCodes) {
        if (starterCodes == null) {
            return null;
        }
        if (starterCodes.isEmpty()) {
            return Collections.emptyMap();
        }

        Map<String, String> normalized = new LinkedHashMap<>();
        starterCodes.forEach((language, snippet) -> {
            String normalizedLanguage = normalizeLanguage(language);
            normalized.put(normalizedLanguage, normalizeStarterCode(normalizedLanguage, snippet));
        });
        return normalized;
    }

    public String normalizeStarterCode(String language, String snippet) {
        if (snippet == null || snippet.isBlank()) {
            return snippet;
        }

        String normalizedLanguage = normalizeLanguage(language);
        if (isExecutableTemplate(normalizedLanguage, snippet)) {
            return ensureStudentPlaceholder(normalizedLanguage, snippet);
        }

        return generateTemplate(normalizedLanguage, snippet);
    }

    public String generateCppTemplatePublic(String snippet) {
        return generateCppTemplate(snippet);
    }

    private String generateTemplate(String language, String snippet) {
        return switch (language) {
            case "cpp" -> generateCppTemplate(snippet);
            case "java" -> generateJavaTemplate(snippet);
            case "javascript" -> generateJavascriptTemplate(snippet);
            case "python" -> generatePythonTemplate(snippet);
            default -> snippet;
        };
    }

    private String normalizeLanguage(String language) {
        if (language == null || language.isBlank()) {
            return "cpp";
        }

        String normalized = language.trim().toLowerCase();
        return switch (normalized) {
            case "c++", "cpp" -> "cpp";
            case "python", "python3", "py" -> "python";
            case "js", "javascript", "node", "nodejs" -> "javascript";
            case "java" -> "java";
            default -> normalized;
        };
    }

    private boolean isExecutableTemplate(String language, String snippet) {
        if (snippet.contains(STUDENT_CODE_PLACEHOLDER)) {
            return true;
        }

        return switch (language) {
            case "cpp", "java" -> snippet.contains("main(");
            case "javascript" -> snippet.contains("fs.readFileSync(0");
            case "python" -> snippet.contains("if __name__ == \"__main__\":");
            default -> false;
        };
    }

    private String ensureStudentPlaceholder(String language, String snippet) {
        if (snippet.contains(STUDENT_CODE_PLACEHOLDER)) {
            return snippet;
        }

        return switch (language) {
            case "cpp", "java", "javascript" -> replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER);
            case "python" -> replacePythonBody(snippet);
            default -> snippet;
        };
    }

    private String generateCppTemplate(String snippet) {
        StringBuilder builder = new StringBuilder();
        String solutionClass = replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();
        CppFunctionSignature signature = parseCppSignature(solutionClass);
        boolean hasSolutionClass = hasCppSolutionClass(solutionClass);

        if (!containsCppIncludes(snippet)) {
            builder.append(CPP_DEFAULT_INCLUDES);
        }
        if (!snippet.contains("using namespace std;")) {
            builder.append("using namespace std;\n");
        }
        if (builder.length() > 0) {
            builder.append("\n");
        }

        if (signature != null) {
            if (usesListNode(signature) && !snippet.contains("struct ListNode")) {
                builder.append(buildListNodeDefinition()).append("\n");
            }
            if (usesTreeNode(signature) && !snippet.contains("struct TreeNode")) {
                builder.append(buildTreeNodeDefinition()).append("\n");
            }
        }

        builder.append(solutionClass);

        if (signature != null && isSupportedCppSignature(signature)) {
            builder.append("\n\n");
            builder.append(buildCppSupportFunctions(signature));
            builder.append("\n");
            builder.append(buildCppMain(signature, hasSolutionClass));
        } else if (!snippet.contains("main(")) {
            builder.append("\n\nint main() {\n");
            builder.append("    return 0;\n");
            builder.append("}\n");
        }

        return builder.toString();
    }

    private boolean containsCppIncludes(String snippet) {
        return snippet.contains("#include <") || snippet.contains("#include\"");
    }

    private boolean hasCppSolutionClass(String snippet) {
        return CPP_SOLUTION_CLASS_PATTERN.matcher(snippet).find();
    }

    private String generateJavaTemplate(String snippet) {
        String solutionClass = replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();
        JavaFunctionSignature signature = parseJavaSignature(solutionClass);
        StringBuilder builder = new StringBuilder();

        builder.append("import java.io.*;\n");
        builder.append("import java.util.*;\n\n");

        if (signature != null) {
            if (usesListNode(signature) && !snippet.contains("class ListNode")) {
                builder.append(buildJavaListNodeDefinition()).append("\n");
            }
            if (usesTreeNode(signature) && !snippet.contains("class TreeNode")) {
                builder.append(buildJavaTreeNodeDefinition()).append("\n");
            }
        }

        builder.append(solutionClass);

        if (signature != null && isSupportedJavaSignature(signature)) {
            builder.append("\n\nclass Main {\n");
            builder.append(buildJavaSupportFunctions(signature));
            builder.append("\n");
            builder.append(buildJavaMain(signature));
            builder.append("}\n");
        } else if (!snippet.contains("main(")) {
            builder.append("\n\nclass Main {\n");
            builder.append("    public static void main(String[] args) throws Exception {\n");
            builder.append("    }\n");
            builder.append("}\n");
        }

        return builder.toString();
    }

    private String generateJavascriptTemplate(String snippet) {
        String functionDefinition = replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();
        JavascriptFunctionSignature signature = parseJavascriptSignature(functionDefinition);

        if (signature == null || !isSupportedJavascriptSignature(signature)) {
            return functionDefinition;
        }

        StringBuilder builder = new StringBuilder();
        builder.append(functionDefinition).append("\n\n");
        builder.append("""
                const fs = require('fs');

                function readLineOrDefault(lines, index) {
                    return index < lines.length ? lines[index] : '';
                }

                function parseNumber(line) {
                    return Number(line.trim());
                }

                function parseBoolean(line) {
                    return line.trim().toLowerCase() === 'true';
                }

                function parseStringValue(line) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
                        return JSON.parse(trimmed);
                    }
                    return trimmed;
                }

                function parseArray(line) {
                    const trimmed = line.trim();
                    if (!trimmed) {
                        return [];
                    }
                    return JSON.parse(trimmed);
                }

                function printResult(result) {
                    if (Array.isArray(result) || (result && typeof result === 'object')) {
                        process.stdout.write(JSON.stringify(result));
                        return;
                    }

                    if (typeof result === 'boolean') {
                        process.stdout.write(result ? 'true' : 'false');
                        return;
                    }

                    process.stdout.write(String(result));
                }

                const rawInput = fs.readFileSync(0, 'utf8');
                const trimmedInput = rawInput.endsWith('\\n') ? rawInput.replace(/\\n$/, '') : rawInput;
                const lines = trimmedInput.length === 0 ? [] : trimmedInput.split(/\\r?\\n/);
                """);

        for (int i = 0; i < signature.parameters().size(); i++) {
            JavascriptParameter parameter = signature.parameters().get(i);
            builder.append("const ")
                    .append(parameter.name())
                    .append(" = ")
                    .append(buildJavascriptParseExpression(parameter.type(), i))
                    .append(";\n");
        }

        builder.append("\nconst result = ")
                .append(signature.functionName())
                .append("(")
                .append(String.join(", ", signature.parameters().stream().map(JavascriptParameter::name).toList()))
                .append(");\n");
        builder.append("printResult(result);\n");
        return builder.toString();
    }

    private String generatePythonTemplate(String snippet) {
        String solutionClass = replacePythonBody(snippet).trim();
        PythonFunctionSignature signature = parsePythonSignature(solutionClass);

        if (signature == null || !isSupportedPythonSignature(signature)) {
            return solutionClass;
        }

        StringBuilder builder = new StringBuilder();
        builder.append("from typing import List, Optional\n");
        builder.append("import ast\n");
        builder.append("import json\n");
        builder.append("from collections import deque\n\n");

        if (usesListNode(signature) && !snippet.contains("class ListNode")) {
            builder.append(buildPythonListNodeDefinition()).append("\n");
        }
        if (usesTreeNode(signature) && !snippet.contains("class TreeNode")) {
            builder.append(buildPythonTreeNodeDefinition()).append("\n");
        }

        builder.append(solutionClass).append("\n\n");
        builder.append(buildPythonSupportFunctions(signature));
        builder.append("\n");
        builder.append(buildPythonMain(signature));
        return builder.toString();
    }

    private String replaceBraceBody(String snippet, String placeholder) {
        Matcher matcher = Pattern.compile("\\([^)]*\\)\\s*\\{").matcher(snippet);
        if (!matcher.find()) {
            return snippet;
        }

        int openBrace = snippet.indexOf('{', matcher.start());
        int closeBrace = findMatchingBrace(snippet, openBrace);
        if (openBrace == -1 || closeBrace == -1) {
            return snippet;
        }

        String indentation = detectIndentation(snippet, openBrace);
        return snippet.substring(0, openBrace + 1)
                + "\n"
                + indentation
                + placeholder
                + "\n"
                + snippet.substring(closeBrace);
    }

    private String replacePythonBody(String snippet) {
        Matcher matcher = PYTHON_METHOD_PATTERN.matcher(snippet);
        if (!matcher.find()) {
            return snippet;
        }

        int bodyStart = matcher.end();
        int bodyEnd = findNextPythonDefinition(snippet, bodyStart);
        String replacement = "\n        " + STUDENT_CODE_PLACEHOLDER + "\n";

        if (bodyEnd == -1) {
            return snippet.substring(0, bodyStart) + replacement;
        }

        return snippet.substring(0, bodyStart) + replacement + snippet.substring(bodyEnd);
    }

    private int findMatchingBrace(String code, int openBrace) {
        int depth = 0;
        for (int i = openBrace; i < code.length(); i++) {
            char current = code.charAt(i);
            if (current == '{') {
                depth++;
            } else if (current == '}') {
                depth--;
                if (depth == 0) {
                    return i;
                }
            }
        }
        return -1;
    }

    private String detectIndentation(String snippet, int openBrace) {
        int lineStart = snippet.lastIndexOf('\n', openBrace);
        String line = lineStart == -1
                ? snippet.substring(0, openBrace)
                : snippet.substring(lineStart + 1, openBrace);

        int leadingSpaces = 0;
        while (leadingSpaces < line.length() && Character.isWhitespace(line.charAt(leadingSpaces))) {
            leadingSpaces++;
        }

        return " ".repeat(leadingSpaces + 4);
    }

    private int findNextPythonDefinition(String code, int fromIndex) {
        Matcher matcher = Pattern.compile("(?m)^\\s*(def|class|if __name__ == )").matcher(code);
        while (matcher.find()) {
            if (matcher.start() > fromIndex) {
                return matcher.start();
            }
        }
        return -1;
    }

    private CppFunctionSignature parseCppSignature(String snippet) {
        String normalizedSnippet = snippet.replaceAll("(?m)^\\s*(public|private|protected)\\s*:\\s*$", "");
        Matcher matcher = CPP_METHOD_PATTERN.matcher(normalizedSnippet);
        if (!matcher.find()) {
            return null;
        }

        String returnType = normalizeType(matcher.group(1));
        String functionName = matcher.group(2).trim();
        List<GenericParameter> parameters = parseParameters(matcher.group(3));
        if (parameters == null) {
            return null;
        }

        return new CppFunctionSignature(returnType, functionName, parameters.stream()
                .map(parameter -> new CppParameter(normalizeType(parameter.type()), parameter.name()))
                .toList());
    }

    private JavaFunctionSignature parseJavaSignature(String snippet) {
        Matcher matcher = JAVA_METHOD_PATTERN.matcher(snippet);
        if (!matcher.find()) {
            return null;
        }

        String returnType = normalizeType(matcher.group(2));
        String functionName = matcher.group(3).trim();
        List<GenericParameter> parameters = parseParameters(matcher.group(4));
        if (parameters == null) {
            return null;
        }

        return new JavaFunctionSignature(returnType, functionName, parameters.stream()
                .map(parameter -> new JavaParameter(normalizeType(parameter.type()), parameter.name()))
                .toList());
    }

    private JavascriptFunctionSignature parseJavascriptSignature(String snippet) {
        Matcher matcher = JS_FUNCTION_PATTERN.matcher(snippet);
        if (!matcher.find()) {
            return null;
        }

        String functionName = matcher.group(1) != null ? matcher.group(1) : matcher.group(3);
        String rawParams = matcher.group(2) != null ? matcher.group(2) : matcher.group(4);
        List<JavascriptParameter> parameters = new ArrayList<>();
        if (rawParams != null && !rawParams.isBlank()) {
            for (String rawParam : rawParams.split(",")) {
                String paramName = rawParam.trim();
                if (!paramName.isBlank()) {
                    parameters.add(new JavascriptParameter(inferJavascriptType(paramName), paramName));
                }
            }
        }

        return new JavascriptFunctionSignature(functionName, parameters);
    }

    private PythonFunctionSignature parsePythonSignature(String snippet) {
        Matcher matcher = PYTHON_METHOD_PATTERN.matcher(snippet);
        if (!matcher.find()) {
            return null;
        }

        String functionName = matcher.group(1).trim();
        String rawParams = matcher.group(2).trim();
        String returnType = matcher.group(3) == null ? "Any" : normalizeType(matcher.group(3));

        List<PythonParameter> parameters = new ArrayList<>();
        if (!rawParams.isBlank()) {
            for (String rawParam : splitParameters(rawParams)) {
                String compact = rawParam.trim();
                if (compact.isBlank() || "self".equals(compact)) {
                    continue;
                }

                String[] parts = compact.split(":", 2);
                String name = parts[0].trim();
                String type = parts.length > 1 ? normalizeType(parts[1]) : inferPythonType(name);
                parameters.add(new PythonParameter(type, name));
            }
        }

        return new PythonFunctionSignature(returnType, functionName, parameters);
    }

    private List<GenericParameter> parseParameters(String rawParams) {
        List<GenericParameter> parameters = new ArrayList<>();
        if (rawParams == null || rawParams.isBlank()) {
            return parameters;
        }

        for (String rawParam : splitParameters(rawParams)) {
            String compact = rawParam.replaceAll("\\s+", " ").trim();
            Matcher matcher = Pattern.compile("(.+?)\\s+([a-zA-Z_][\\w]*)$").matcher(compact);
            if (!matcher.find()) {
                return null;
            }
            parameters.add(new GenericParameter(matcher.group(1).trim(), matcher.group(2).trim()));
        }

        return parameters;
    }

    private List<String> splitParameters(String rawParams) {
        List<String> parts = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        int angleDepth = 0;
        int bracketDepth = 0;

        for (int i = 0; i < rawParams.length(); i++) {
            char ch = rawParams.charAt(i);
            if (ch == '<') {
                angleDepth++;
            } else if (ch == '>') {
                angleDepth--;
            } else if (ch == '[') {
                bracketDepth++;
            } else if (ch == ']') {
                bracketDepth--;
            } else if (ch == ',' && angleDepth == 0 && bracketDepth == 0) {
                parts.add(current.toString());
                current.setLength(0);
                continue;
            }
            current.append(ch);
        }

        if (!current.isEmpty()) {
            parts.add(current.toString());
        }
        return parts;
    }

    private String normalizeType(String type) {
        return type
                .replaceAll("(?m)\\b(public|private|protected|final|static)\\b", "")
                .replaceAll("\\s+", " ")
                .replace(" <", "<")
                .replace("< ", "<")
                .replace(" >", ">")
                .replace("> ", ">")
                .replace(" &", "&")
                .replace("& ", "&")
                .replace(" *", "*")
                .replace("* ", "*")
                .trim();
    }

    private boolean isSupportedCppSignature(CppFunctionSignature signature) {
        if (!isSupportedCppReturnType(signature.returnType())) {
            return false;
        }
        return signature.parameters().stream()
                .allMatch(parameter -> isSupportedCppParameterType(parameter.type()))
                && signature.parameters().size() <= 3;
    }

    private boolean isSupportedCppReturnType(String type) {
        return switch (type) {
            case "int", "long", "bool", "double", "string",
                    "vector<int>", "vector<long long>", "vector<string>",
                    "ListNode*", "TreeNode*" -> true;
            default -> false;
        };
    }

    private boolean isSupportedCppParameterType(String type) {
        return switch (type) {
            case "int", "long", "bool", "double", "string", "const string&",
                    "vector<int>", "vector<int>&", "const vector<int>&",
                    "vector<long long>", "vector<long long>&", "const vector<long long>&",
                    "vector<string>", "vector<string>&", "const vector<string>&",
                    "ListNode*", "TreeNode*" -> true;
            default -> false;
        };
    }

    private boolean isSupportedJavaSignature(JavaFunctionSignature signature) {
        if (!isSupportedJavaType(signature.returnType())) {
            return false;
        }
        return signature.parameters().stream()
                .allMatch(parameter -> isSupportedJavaType(parameter.type()))
                && signature.parameters().size() <= 3;
    }

    private boolean isSupportedJavascriptSignature(JavascriptFunctionSignature signature) {
        return signature.parameters().size() <= 3;
    }

    private boolean isSupportedPythonSignature(PythonFunctionSignature signature) {
        if (!isSupportedPythonType(signature.returnType())) {
            return false;
        }
        return signature.parameters().stream()
                .allMatch(parameter -> isSupportedPythonType(parameter.type()))
                && signature.parameters().size() <= 3;
    }

    private boolean isSupportedJavaType(String type) {
        return switch (type) {
            case "int", "long", "boolean", "double", "String", "int[]", "long[]",
                    "List<Integer>", "List<String>", "ListNode", "TreeNode" -> true;
            default -> false;
        };
    }

    private boolean isSupportedPythonType(String type) {
        return switch (type) {
            case "int", "str", "bool", "float", "List[int]", "List[str]",
                    "Optional[ListNode]", "Optional[TreeNode]" -> true;
            default -> false;
        };
    }

    private String buildCppSupportFunctions(CppFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        boolean needsVectorIntParser = hasCppParameterType(signature, "vector<int>");
        boolean needsVectorLongParser = hasCppParameterType(signature, "vector<long long>");
        boolean needsVectorStringParser = hasCppParameterType(signature, "vector<string>");
        boolean needsIntParser = hasCppParameterType(signature, "int");
        boolean needsLongParser = hasCppParameterType(signature, "long");
        boolean needsBoolParser = hasCppParameterType(signature, "bool");
        boolean needsDoubleParser = hasCppParameterType(signature, "double");
        boolean needsStringParser = hasCppParameterType(signature, "string");
        boolean needsVectorPrinter = isCppReturnType(signature, "vector<int>")
                || isCppReturnType(signature, "vector<long long>")
                || isCppReturnType(signature, "vector<string>");
        boolean needsListNode = usesListNode(signature);
        boolean needsTreeNode = usesTreeNode(signature);

        builder.append("""
                static string trim(const string& value) {
                    size_t start = value.find_first_not_of(" \\t\\r\\n");
                    if (start == string::npos) {
                        return "";
                    }

                    size_t end = value.find_last_not_of(" \\t\\r\\n");
                    return value.substr(start, end - start + 1);
                }

                static string readLineOrDefault(const vector<string>& lines, size_t index) {
                    return index < lines.size() ? lines[index] : "";
                }

                static string escapeString(const string& value) {
                    string escaped;
                    for (char ch : value) {
                        switch (ch) {
                            case '\\\\':
                                escaped += '\\\\';
                                escaped += '\\\\';
                                break;
                            case '"':
                                escaped += '\\\\';
                                escaped += '"';
                                break;
                            case '\\n':
                                escaped += '\\\\';
                                escaped += 'n';
                                break;
                            case '\\r':
                                escaped += '\\\\';
                                escaped += 'r';
                                break;
                            case '\\t':
                                escaped += '\\\\';
                                escaped += 't';
                                break;
                            default:
                                escaped += ch;
                                break;
                        }
                    }
                    return escaped;
                }

                template <typename T>
                static void printValue(const T& value) {
                    cout << value;
                }

                static void printValue(const string& value) {
                    cout << '"' << escapeString(value) << '"';
                }
                """);

        if (needsVectorIntParser || needsListNode) {
            builder.append("""

                    static vector<int> parseVectorInt(string line) {
                        line = trim(line);
                        if (!line.empty() && line.front() == '[' && line.back() == ']') {
                            line = line.substr(1, line.size() - 2);
                        }

                        vector<int> values;
                        string current;
                        stringstream ss(line);
                        while (getline(ss, current, ',')) {
                            current = trim(current);
                            if (!current.empty()) {
                                values.push_back(stoi(current));
                            }
                        }
                        return values;
                    }
                    """);
        }

        if (needsVectorLongParser) {
            builder.append("""

                    static vector<long long> parseVectorLong(string line) {
                        line = trim(line);
                        if (!line.empty() && line.front() == '[' && line.back() == ']') {
                            line = line.substr(1, line.size() - 2);
                        }

                        vector<long long> values;
                        string current;
                        stringstream ss(line);
                        while (getline(ss, current, ',')) {
                            current = trim(current);
                            if (!current.empty()) {
                                values.push_back(stoll(current));
                            }
                        }
                        return values;
                    }
                    """);
        }

        if (needsVectorStringParser) {
            builder.append("""

                    static vector<string> parseVectorString(string line) {
                        line = trim(line);
                        if (!line.empty() && line.front() == '[' && line.back() == ']') {
                            line = line.substr(1, line.size() - 2);
                        }

                        vector<string> values;
                        string current;
                        stringstream ss(line);
                        while (getline(ss, current, ',')) {
                            current = trim(current);
                            if (current.size() >= 2 && current.front() == '"' && current.back() == '"') {
                                current = current.substr(1, current.size() - 2);
                            }
                            values.push_back(current);
                        }
                        return values;
                    }
                    """);
        }

        if (needsIntParser) {
            builder.append("""

                    static int parseInt(string line) {
                        return stoi(trim(line));
                    }
                    """);
        }

        if (needsLongParser) {
            builder.append("""

                    static long long parseLong(string line) {
                        return stoll(trim(line));
                    }
                    """);
        }

        if (needsBoolParser) {
            builder.append("""

                    static bool parseBool(string line) {
                        line = trim(line);
                        return line == "true" || line == "1";
                    }
                    """);
        }

        if (needsDoubleParser) {
            builder.append("""

                    static double parseDouble(string line) {
                        return stod(trim(line));
                    }
                    """);
        }

        if (needsStringParser) {
            builder.append("""

                    static string parseStringValue(string line) {
                        line = trim(line);
                        if (line.size() >= 2 && line.front() == '"' && line.back() == '"') {
                            return line.substr(1, line.size() - 2);
                        }
                        return line;
                    }
                    """);
        }

        if (needsVectorPrinter) {
            builder.append("""

                    template <typename T>
                    static void printVector(const vector<T>& values) {
                        cout << "[";
                        for (size_t i = 0; i < values.size(); ++i) {
                            if (i > 0) {
                                cout << ",";
                            }
                            printValue(values[i]);
                        }
                        cout << "]";
                    }
                    """);
        }

        if (needsListNode) {
            builder.append("""

                    static ListNode* parseListNode(string line) {
                        vector<int> values = parseVectorInt(line);
                        ListNode dummy(0);
                        ListNode* tail = &dummy;
                        for (int value : values) {
                            tail->next = new ListNode(value);
                            tail = tail->next;
                        }
                        return dummy.next;
                    }
                    """);
            if ("ListNode*".equals(signature.returnType())) {
                builder.append("""

                        static void printListNode(ListNode* head) {
                            cout << "[";
                            bool first = true;
                            while (head != nullptr) {
                                if (!first) {
                                    cout << ",";
                                }
                                cout << head->val;
                                first = false;
                                head = head->next;
                            }
                            cout << "]";
                        }
                        """);
            }
        }

        if (needsTreeNode) {
            builder.append("""

                    static TreeNode* parseTreeNode(string line) {
                        line = trim(line);
                        if (line.empty() || line == "[]" || line == "[null]") {
                            return nullptr;
                        }
                        if (line.front() == '[' && line.back() == ']') {
                            line = line.substr(1, line.size() - 2);
                        }

                        vector<string> values;
                        string current;
                        stringstream ss(line);
                        while (getline(ss, current, ',')) {
                            values.push_back(trim(current));
                        }

                        if (values.empty() || values[0] == "null" || values[0].empty()) {
                            return nullptr;
                        }

                        TreeNode* root = new TreeNode(stoi(values[0]));
                        queue<TreeNode*> nodes;
                        nodes.push(root);
                        size_t index = 1;

                        while (!nodes.empty() && index < values.size()) {
                            TreeNode* node = nodes.front();
                            nodes.pop();

                            if (index < values.size() && values[index] != "null" && !values[index].empty()) {
                                node->left = new TreeNode(stoi(values[index]));
                                nodes.push(node->left);
                            }
                            ++index;

                            if (index < values.size() && values[index] != "null" && !values[index].empty()) {
                                node->right = new TreeNode(stoi(values[index]));
                                nodes.push(node->right);
                            }
                            ++index;
                        }

                        return root;
                    }
                    """);
            if ("TreeNode*".equals(signature.returnType())) {
                builder.append("""

                        static void printTreeNode(TreeNode* root) {
                            if (root == nullptr) {
                                cout << "[]";
                                return;
                            }

                            vector<string> values;
                            queue<TreeNode*> nodes;
                            nodes.push(root);

                            while (!nodes.empty()) {
                                TreeNode* node = nodes.front();
                                nodes.pop();

                                if (node == nullptr) {
                                    values.push_back("null");
                                    continue;
                                }

                                values.push_back(to_string(node->val));
                                nodes.push(node->left);
                                nodes.push(node->right);
                            }

                            while (!values.empty() && values.back() == "null") {
                                values.pop_back();
                            }

                            cout << "[";
                            for (size_t i = 0; i < values.size(); ++i) {
                                if (i > 0) {
                                    cout << ",";
                                }
                                cout << values[i];
                            }
                            cout << "]";
                        }
                        """);
            }
        }

        return builder.toString();
    }

    private String buildCppMain(CppFunctionSignature signature, boolean hasSolutionClass) {
        StringBuilder builder = new StringBuilder();
        builder.append("int main() {\n");
        builder.append("    ios::sync_with_stdio(false);\n");
        builder.append("    cin.tie(nullptr);\n\n");
        builder.append("    vector<string> lines;\n");
        builder.append("    string line;\n");
        builder.append("    for (size_t i = 0; i < ").append(signature.parameters().size()).append("; ++i) {\n");
        builder.append("        if (getline(cin, line)) {\n");
        builder.append("            lines.push_back(line);\n");
        builder.append("        } else {\n");
        builder.append("            lines.push_back(\"\");\n");
        builder.append("        }\n");
        builder.append("    }\n\n");

        for (int i = 0; i < signature.parameters().size(); i++) {
            CppParameter parameter = signature.parameters().get(i);
            builder.append("    ")
                    .append(toCppStorageType(parameter.type()))
                    .append(" ")
                    .append(parameter.name())
                    .append(" = ")
                    .append(buildCppParseExpression(parameter.type(), i))
                    .append(";\n");
        }

        String callArguments = String.join(", ", signature.parameters().stream().map(CppParameter::name).toList());
        if (hasSolutionClass) {
            builder.append("\n    Solution solution;\n");
            builder.append("    auto result = solution.")
                    .append(signature.functionName())
                    .append("(")
                    .append(callArguments)
                    .append(");\n");
        } else {
            builder.append("\n    auto result = ")
                    .append(signature.functionName())
                    .append("(")
                    .append(callArguments)
                    .append(");\n");
        }
        builder.append(buildCppPrintStatement(signature.returnType()));
        builder.append("\n    return 0;\n");
        builder.append("}\n");
        return builder.toString();
    }

    private String buildCppParseExpression(String type, int index) {
        String source = "readLineOrDefault(lines, " + index + ")";
        return switch (type) {
            case "int" -> "parseInt(" + source + ")";
            case "long" -> "parseLong(" + source + ")";
            case "bool" -> "parseBool(" + source + ")";
            case "double" -> "parseDouble(" + source + ")";
            case "string" -> "parseStringValue(" + source + ")";
            case "vector<int>" -> "parseVectorInt(" + source + ")";
            case "vector<long long>" -> "parseVectorLong(" + source + ")";
            case "vector<string>" -> "parseVectorString(" + source + ")";
            case "ListNode*" -> "parseListNode(" + source + ")";
            case "TreeNode*" -> "parseTreeNode(" + source + ")";
            default -> source;
        };
    }

    private String buildCppPrintStatement(String returnType) {
        return switch (returnType) {
            case "int", "long", "double" -> "    cout << result;\n";
            case "string" -> "    printValue(result);\n";
            case "bool" -> "    cout << (result ? \"true\" : \"false\");\n";
            case "vector<int>", "vector<long long>", "vector<string>" -> "    printVector(result);\n";
            case "ListNode*" -> "    printListNode(result);\n";
            case "TreeNode*" -> "    printTreeNode(result);\n";
            default -> "    // Unsupported return type for auto runner.\n";
        };
    }

    private String toCppStorageType(String type) {
        return switch (type) {
            case "vector<int>&", "const vector<int>&" -> "vector<int>";
            case "vector<long long>&", "const vector<long long>&" -> "vector<long long>";
            case "vector<string>&", "const vector<string>&" -> "vector<string>";
            case "const string&" -> "string";
            case "long" -> "long long";
            default -> type;
        };
    }

    private String buildJavaSupportFunctions(JavaFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        boolean needsIntArray = usesJavaType(signature, "int[]");
        boolean needsLongArray = usesJavaType(signature, "long[]");
        boolean needsIntegerList = usesJavaType(signature, "List<Integer>");
        boolean needsStringList = usesJavaType(signature, "List<String>");
        boolean needsListNode = usesListNode(signature);
        boolean needsTreeNode = usesTreeNode(signature);

        builder.append("""
                    private static String readLineOrDefault(List<String> lines, int index) {
                        return index < lines.size() ? lines.get(index) : "";
                    }

                    private static String trim(String value) {
                        return value == null ? "" : value.trim();
                    }

                    private static int parseInt(String line) {
                        return Integer.parseInt(trim(line));
                    }

                    private static long parseLong(String line) {
                        return Long.parseLong(trim(line));
                    }

                    private static boolean parseBoolean(String line) {
                        String normalized = trim(line).toLowerCase(Locale.ROOT);
                        return "true".equals(normalized) || "1".equals(normalized);
                    }

                    private static double parseDouble(String line) {
                        return Double.parseDouble(trim(line));
                    }

                    private static String parseStringValue(String line) {
                        String value = trim(line);
                        if (value.length() >= 2 && value.startsWith("\"") && value.endsWith("\"")) {
                            return value.substring(1, value.length() - 1);
                        }
                        return value;
                    }
                """);

        if (needsIntArray || needsIntegerList || needsListNode) {
            builder.append("""

                        private static int[] parseIntArray(String line) {
                            String value = trim(line);
                            if (value.length() >= 2 && value.startsWith("[") && value.endsWith("]")) {
                                value = value.substring(1, value.length() - 1);
                            }

                            if (value.isBlank()) {
                                return new int[0];
                            }

                            String[] tokens = value.split(",");
                            int[] numbers = new int[tokens.length];
                            for (int i = 0; i < tokens.length; i++) {
                                numbers[i] = Integer.parseInt(tokens[i].trim());
                            }
                            return numbers;
                        }
                    """);
        }

        if (needsLongArray) {
            builder.append("""

                        private static long[] parseLongArray(String line) {
                            String value = trim(line);
                            if (value.length() >= 2 && value.startsWith("[") && value.endsWith("]")) {
                                value = value.substring(1, value.length() - 1);
                            }

                            if (value.isBlank()) {
                                return new long[0];
                            }

                            String[] tokens = value.split(",");
                            long[] numbers = new long[tokens.length];
                            for (int i = 0; i < tokens.length; i++) {
                                numbers[i] = Long.parseLong(tokens[i].trim());
                            }
                            return numbers;
                        }
                    """);
        }

        if (needsIntegerList) {
            builder.append("""

                        private static List<Integer> parseIntegerList(String line) {
                            int[] numbers = parseIntArray(line);
                            List<Integer> values = new ArrayList<>(numbers.length);
                            for (int number : numbers) {
                                values.add(number);
                            }
                            return values;
                        }
                    """);
        }

        if (needsStringList) {
            builder.append("""

                        private static List<String> parseStringList(String line) {
                            String value = trim(line);
                            if (value.length() >= 2 && value.startsWith("[") && value.endsWith("]")) {
                                value = value.substring(1, value.length() - 1);
                            }

                            List<String> values = new ArrayList<>();
                            if (value.isBlank()) {
                                return values;
                            }

                            for (String token : value.split(",")) {
                                String current = token.trim();
                                if (current.length() >= 2 && current.startsWith("\"") && current.endsWith("\"")) {
                                    current = current.substring(1, current.length() - 1);
                                }
                                values.add(current);
                            }
                            return values;
                        }
                    """);
        }

        if (needsListNode) {
            builder.append("""

                        private static ListNode parseListNode(String line) {
                            int[] values = parseIntArray(line);
                            ListNode dummy = new ListNode(0);
                            ListNode tail = dummy;
                            for (int value : values) {
                                tail.next = new ListNode(value);
                                tail = tail.next;
                            }
                            return dummy.next;
                        }
                    """);
        }

        if (needsTreeNode) {
            builder.append("""

                        private static TreeNode parseTreeNode(String line) {
                            String value = trim(line);
                            if (value.isBlank() || "[]".equals(value) || "[null]".equals(value)) {
                                return null;
                            }
                            if (value.length() >= 2 && value.startsWith("[") && value.endsWith("]")) {
                                value = value.substring(1, value.length() - 1);
                            }

                            String[] tokens = value.split(",");
                            if (tokens.length == 0 || trim(tokens[0]).isEmpty() || "null".equals(trim(tokens[0]))) {
                                return null;
                            }

                            TreeNode root = new TreeNode(Integer.parseInt(trim(tokens[0])));
                            Queue<TreeNode> queue = new ArrayDeque<>();
                            queue.add(root);
                            int index = 1;

                            while (!queue.isEmpty() && index < tokens.length) {
                                TreeNode node = queue.poll();
                                if (node == null) {
                                    continue;
                                }

                                if (index < tokens.length) {
                                    String left = trim(tokens[index++]);
                                    if (!left.isEmpty() && !"null".equals(left)) {
                                        node.left = new TreeNode(Integer.parseInt(left));
                                        queue.add(node.left);
                                    }
                                }

                                if (index < tokens.length) {
                                    String right = trim(tokens[index++]);
                                    if (!right.isEmpty() && !"null".equals(right)) {
                                        node.right = new TreeNode(Integer.parseInt(right));
                                        queue.add(node.right);
                                    }
                                }
                            }

                            return root;
                        }
                    """);
        }

        builder.append("""

                    private static void printResult(Object result) {
                        if (result == null) {
                            System.out.print("null");
                            return;
                        }

                        if (result instanceof Boolean booleanValue) {
                            System.out.print(booleanValue ? "true" : "false");
                            return;
                        }

                        if (result instanceof int[] values) {
                            System.out.print("[");
                            for (int i = 0; i < values.length; i++) {
                                if (i > 0) {
                                    System.out.print(",");
                                }
                                System.out.print(values[i]);
                            }
                            System.out.print("]");
                            return;
                        }

                        if (result instanceof long[] values) {
                            System.out.print("[");
                            for (int i = 0; i < values.length; i++) {
                                if (i > 0) {
                                    System.out.print(",");
                                }
                                System.out.print(values[i]);
                            }
                            System.out.print("]");
                            return;
                        }

                        if (result instanceof List<?> values) {
                            System.out.print("[");
                            for (int i = 0; i < values.size(); i++) {
                                if (i > 0) {
                                    System.out.print(",");
                                }
                                System.out.print(values.get(i));
                            }
                            System.out.print("]");
                            return;
                        }

                        if (result instanceof ListNode node) {
                            System.out.print("[");
                            boolean first = true;
                            while (node != null) {
                                if (!first) {
                                    System.out.print(",");
                                }
                                System.out.print(node.val);
                                first = false;
                                node = node.next;
                            }
                            System.out.print("]");
                            return;
                        }

                        if (result instanceof TreeNode root) {
                            List<String> values = new ArrayList<>();
                            Queue<TreeNode> queue = new ArrayDeque<>();
                            queue.add(root);
                            while (!queue.isEmpty()) {
                                TreeNode node = queue.poll();
                                if (node == null) {
                                    values.add("null");
                                    continue;
                                }
                                values.add(String.valueOf(node.val));
                                queue.add(node.left);
                                queue.add(node.right);
                            }
                            while (!values.isEmpty() && "null".equals(values.get(values.size() - 1))) {
                                values.remove(values.size() - 1);
                            }
                            System.out.print("[" + String.join(",", values) + "]");
                            return;
                        }

                        System.out.print(result);
                    }
                """);

        return builder.toString();
    }

    private String buildJavaMain(JavaFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        builder.append("    public static void main(String[] args) throws Exception {\n");
        builder.append("        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));\n");
        builder.append("        List<String> lines = new ArrayList<>();\n");
        builder.append("        for (int i = 0; i < ").append(signature.parameters().size()).append("; i++) {\n");
        builder.append("            String line = reader.readLine();\n");
        builder.append("            lines.add(line == null ? \"\" : line);\n");
        builder.append("        }\n\n");

        for (int i = 0; i < signature.parameters().size(); i++) {
            JavaParameter parameter = signature.parameters().get(i);
            builder.append("        ")
                    .append(toJavaStorageType(parameter.type()))
                    .append(" ")
                    .append(parameter.name())
                    .append(" = ")
                    .append(buildJavaParseExpression(parameter.type(), i))
                    .append(";\n");
        }

        builder.append("\n        Solution solution = new Solution();\n");
        builder.append("        var result = solution.")
                .append(signature.functionName())
                .append("(")
                .append(String.join(", ", signature.parameters().stream().map(JavaParameter::name).toList()))
                .append(");\n");
        builder.append("        printResult(result);\n");
        builder.append("    }\n");
        return builder.toString();
    }

    private String buildJavaParseExpression(String type, int index) {
        String source = "readLineOrDefault(lines, " + index + ")";
        return switch (type) {
            case "int" -> "parseInt(" + source + ")";
            case "long" -> "parseLong(" + source + ")";
            case "boolean" -> "parseBoolean(" + source + ")";
            case "double" -> "parseDouble(" + source + ")";
            case "String" -> "parseStringValue(" + source + ")";
            case "int[]" -> "parseIntArray(" + source + ")";
            case "long[]" -> "parseLongArray(" + source + ")";
            case "List<Integer>" -> "parseIntegerList(" + source + ")";
            case "List<String>" -> "parseStringList(" + source + ")";
            case "ListNode" -> "parseListNode(" + source + ")";
            case "TreeNode" -> "parseTreeNode(" + source + ")";
            default -> source;
        };
    }

    private String toJavaStorageType(String type) {
        return type;
    }

    private String buildJavascriptParseExpression(String type, int index) {
        String source = "readLineOrDefault(lines, " + index + ")";
        return switch (type) {
            case "number" -> "parseNumber(" + source + ")";
            case "boolean" -> "parseBoolean(" + source + ")";
            case "string" -> "parseStringValue(" + source + ")";
            default -> "parseArray(" + source + ")";
        };
    }

    private String buildPythonSupportFunctions(PythonFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        builder.append("""
                def read_line_or_default(lines, index):
                    return lines[index] if index < len(lines) else ""

                def parse_scalar(line):
                    value = line.strip()
                    if value == "":
                        return value
                    try:
                        return ast.literal_eval(value)
                    except Exception:
                        return value

                def parse_list_node(line):
                    values = parse_scalar(line)
                    if not values:
                        return None
                    dummy = ListNode(0)
                    tail = dummy
                    for value in values:
                        tail.next = ListNode(value)
                        tail = tail.next
                    return dummy.next

                def parse_tree_node(line):
                    values = parse_scalar(line)
                    if not values:
                        return None
                    root = TreeNode(values[0])
                    queue = deque([root])
                    index = 1
                    while queue and index < len(values):
                        node = queue.popleft()
                        if node is None:
                            continue
                        if index < len(values) and values[index] is not None:
                            node.left = TreeNode(values[index])
                            queue.append(node.left)
                        index += 1
                        if index < len(values) and values[index] is not None:
                            node.right = TreeNode(values[index])
                            queue.append(node.right)
                        index += 1
                    return root

                def print_result(result):
                    if isinstance(result, bool):
                        print(str(result).lower(), end="")
                        return
                    if isinstance(result, list):
                        print(json.dumps(result, separators=(',', ':')), end="")
                        return
                    if isinstance(result, ListNode):
                        values = []
                        while result is not None:
                            values.append(result.val)
                            result = result.next
                        print(json.dumps(values, separators=(',', ':')), end="")
                        return
                    if isinstance(result, TreeNode):
                        values = []
                        queue = deque([result])
                        while queue:
                            node = queue.popleft()
                            if node is None:
                                values.append(None)
                                continue
                            values.append(node.val)
                            queue.append(node.left)
                            queue.append(node.right)
                        while values and values[-1] is None:
                            values.pop()
                        print(json.dumps(values, separators=(',', ':')), end="")
                        return
                    print(result, end="")
                """);
        return builder.toString();
    }

    private String buildPythonMain(PythonFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        builder.append("if __name__ == \"__main__\":\n");
        builder.append("    import sys\n");
        builder.append("    raw_input = sys.stdin.read()\n");
        builder.append("    lines = [] if raw_input == \"\" else raw_input.rstrip(\"\\n\").splitlines()\n");
        for (int i = 0; i < signature.parameters().size(); i++) {
            PythonParameter parameter = signature.parameters().get(i);
            builder.append("    ")
                    .append(parameter.name())
                    .append(" = ")
                    .append(buildPythonParseExpression(parameter.type(), i))
                    .append("\n");
        }
        builder.append("\n    solution = Solution()\n");
        builder.append("    result = solution.")
                .append(signature.functionName())
                .append("(")
                .append(String.join(", ", signature.parameters().stream().map(PythonParameter::name).toList()))
                .append(")\n");
        builder.append("    print_result(result)\n");
        return builder.toString();
    }

    private String buildPythonParseExpression(String type, int index) {
        String source = "read_line_or_default(lines, " + index + ")";
        return switch (type) {
            case "Optional[ListNode]" -> "parse_list_node(" + source + ")";
            case "Optional[TreeNode]" -> "parse_tree_node(" + source + ")";
            default -> "parse_scalar(" + source + ")";
        };
    }

    private String inferJavascriptType(String paramName) {
        String normalized = paramName.toLowerCase();
        if (normalized.contains("target") || normalized.contains("num") || "k".equals(normalized) || "n".equals(normalized)) {
            return "number";
        }
        if (normalized.contains("flag") || normalized.startsWith("is")) {
            return "boolean";
        }
        if (normalized.contains("str") || normalized.contains("word") || normalized.contains("s")) {
            return "string";
        }
        return "array";
    }

    private String inferPythonType(String paramName) {
        String normalized = paramName.toLowerCase();
        if ("n".equals(normalized) || normalized.endsWith("count") || normalized.contains("target")) {
            return "int";
        }
        if (normalized.contains("nums") || normalized.contains("values")) {
            return "List[int]";
        }
        if ("s".equals(normalized) || normalized.contains("word")) {
            return "str";
        }
        return "int";
    }

    private boolean usesCppType(CppFunctionSignature signature, String type) {
        if (matchesCppType(signature.returnType(), type)) {
            return true;
        }
        return signature.parameters().stream().anyMatch(parameter -> matchesCppType(parameter.type(), type));
    }

    private boolean hasCppParameterType(CppFunctionSignature signature, String type) {
        return signature.parameters().stream().anyMatch(parameter -> matchesCppType(parameter.type(), type));
    }

    private boolean isCppReturnType(CppFunctionSignature signature, String type) {
        return matchesCppType(signature.returnType(), type);
    }

    private boolean matchesCppType(String type, String candidate) {
        return type.equals(candidate)
                || type.equals(candidate + "&")
                || type.equals("const " + candidate + "&");
    }

    private boolean usesJavaType(JavaFunctionSignature signature, String type) {
        if (type.equals(signature.returnType())) {
            return true;
        }
        return signature.parameters().stream().anyMatch(parameter -> type.equals(parameter.type()));
    }

    private boolean usesListNode(CppFunctionSignature signature) {
        return usesCppType(signature, "ListNode*");
    }

    private boolean usesTreeNode(CppFunctionSignature signature) {
        return usesCppType(signature, "TreeNode*");
    }

    private boolean usesListNode(JavaFunctionSignature signature) {
        return usesJavaType(signature, "ListNode");
    }

    private boolean usesTreeNode(JavaFunctionSignature signature) {
        return usesJavaType(signature, "TreeNode");
    }

    private boolean usesListNode(PythonFunctionSignature signature) {
        return "Optional[ListNode]".equals(signature.returnType())
                || signature.parameters().stream().anyMatch(parameter -> "Optional[ListNode]".equals(parameter.type()));
    }

    private boolean usesTreeNode(PythonFunctionSignature signature) {
        return "Optional[TreeNode]".equals(signature.returnType())
                || signature.parameters().stream().anyMatch(parameter -> "Optional[TreeNode]".equals(parameter.type()));
    }

    private String buildListNodeDefinition() {
        return """
                struct ListNode {
                    int val;
                    ListNode *next;
                    ListNode() : val(0), next(nullptr) {}
                    ListNode(int x) : val(x), next(nullptr) {}
                    ListNode(int x, ListNode *next) : val(x), next(next) {}
                };
                """;
    }

    private String buildTreeNodeDefinition() {
        return """
                struct TreeNode {
                    int val;
                    TreeNode *left;
                    TreeNode *right;
                    TreeNode() : val(0), left(nullptr), right(nullptr) {}
                    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
                    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
                };
                """;
    }

    private String buildJavaListNodeDefinition() {
        return """
                class ListNode {
                    int val;
                    ListNode next;

                    ListNode() {}

                    ListNode(int val) {
                        this.val = val;
                    }

                    ListNode(int val, ListNode next) {
                        this.val = val;
                        this.next = next;
                    }
                }
                """;
    }

    private String buildJavaTreeNodeDefinition() {
        return """
                class TreeNode {
                    int val;
                    TreeNode left;
                    TreeNode right;

                    TreeNode() {}

                    TreeNode(int val) {
                        this.val = val;
                    }

                    TreeNode(int val, TreeNode left, TreeNode right) {
                        this.val = val;
                        this.left = left;
                        this.right = right;
                    }
                }
                """;
    }

    private String buildPythonListNodeDefinition() {
        return """
                class ListNode:
                    def __init__(self, val=0, next=None):
                        self.val = val
                        self.next = next
                """;
    }

    private String buildPythonTreeNodeDefinition() {
        return """
                class TreeNode:
                    def __init__(self, val=0, left=None, right=None):
                        self.val = val
                        self.left = left
                        self.right = right
                """;
    }

    private record GenericParameter(String type, String name) {
    }

    private record CppFunctionSignature(String returnType, String functionName, List<CppParameter> parameters) {
    }

    private record CppParameter(String type, String name) {
    }

    private record JavaFunctionSignature(String returnType, String functionName, List<JavaParameter> parameters) {
    }

    private record JavaParameter(String type, String name) {
    }

    private record JavascriptFunctionSignature(String functionName, List<JavascriptParameter> parameters) {
    }

    private record JavascriptParameter(String type, String name) {
    }

    private record PythonFunctionSignature(String returnType, String functionName, List<PythonParameter> parameters) {
    }

    private record PythonParameter(String type, String name) {
    }
}
