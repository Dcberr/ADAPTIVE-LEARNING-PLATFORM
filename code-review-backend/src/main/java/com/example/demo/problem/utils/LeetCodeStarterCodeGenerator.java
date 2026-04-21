package com.example.demo.problem.utils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.stereotype.Component;

@Component
public class LeetCodeStarterCodeGenerator {

    private static final String STUDENT_CODE_PLACEHOLDER = "//STUDENT_CODE_HERE";
    private static final Pattern CPP_METHOD_PATTERN = Pattern.compile(
            "([a-zA-Z_][\\w:<>,\\s&*]*?)\\s+([a-zA-Z_][\\w]*)\\s*\\(([^)]*)\\)\\s*\\{"
    );

    public Map<String, String> generateStarterCodes(String leetCodeLanguage, String leetCodeCodeSnippet) {
        if (leetCodeCodeSnippet == null || leetCodeCodeSnippet.isBlank()) {
            return Collections.emptyMap();
        }

        String normalizedLanguage = normalizeLanguage(leetCodeLanguage);
        return Map.of(normalizedLanguage, generateTemplate(normalizedLanguage, leetCodeCodeSnippet));
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
            case "python", "python3" -> "python";
            case "js", "javascript", "node", "nodejs" -> "javascript";
            case "java" -> "java";
            default -> normalized;
        };
    }

    private String generateCppTemplate(String snippet) {
        StringBuilder builder = new StringBuilder();
        String solutionClass = replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();
        CppFunctionSignature signature = parseCppSignature(solutionClass);

        if (!snippet.contains("#include <bits/stdc++.h>")) {
            builder.append("#include <bits/stdc++.h>\n");
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
            builder.append(buildCppMain(signature));
        } else if (!snippet.contains("main(")) {
            builder.append("\n\nint main() {\n");
            builder.append("    // Imported from LeetCode. Add validated stdin parsing here if you want custom input run.\n");
            builder.append("    return 0;\n");
            builder.append("}\n");
        }

        return builder.toString();
    }

    private String generateJavaTemplate(String snippet) {
        String template = replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();

        if (template.contains("public static void main(")) {
            return template;
        }

        return template + "\n\nclass Main {\n"
                + "    public static void main(String[] args) {\n"
                + "        // Imported from LeetCode. Add stdin parsing here if needed.\n"
                + "    }\n"
                + "}\n";
    }

    private String generateJavascriptTemplate(String snippet) {
        return replaceBraceBody(snippet, STUDENT_CODE_PLACEHOLDER).trim();
    }

    private String generatePythonTemplate(String snippet) {
        return replacePythonBody(snippet).trim();
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
        Matcher matcher = Pattern.compile("(?m)^(\\s*def\\s+\\w+\\s*\\([^)]*\\)\\s*:\\s*)$").matcher(snippet);
        if (!matcher.find()) {
            return snippet;
        }

        int bodyStart = matcher.end();
        int bodyEnd = findNextPythonDefinition(snippet, bodyStart);
        String replacement = "\n        pass\n";

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
        Matcher matcher = Pattern.compile("(?m)^\\s*(def|class)\\s+").matcher(code);
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

        String returnType = normalizeCppType(matcher.group(1));
        String functionName = matcher.group(2).trim();
        String rawParams = matcher.group(3).trim();

        List<CppParameter> parameters = new ArrayList<>();
        if (!rawParams.isBlank()) {
            for (String rawParam : rawParams.split(",")) {
                CppParameter parameter = parseCppParameter(rawParam.trim());
                if (parameter == null) {
                    return null;
                }
                parameters.add(parameter);
            }
        }

        return new CppFunctionSignature(returnType, functionName, parameters);
    }

    private CppParameter parseCppParameter(String rawParam) {
        String compact = rawParam.replaceAll("\\s+", " ").trim();
        Matcher matcher = Pattern.compile("(.+?)\\s+([a-zA-Z_][\\w]*)$").matcher(compact);
        if (!matcher.find()) {
            return null;
        }

        return new CppParameter(normalizeCppType(matcher.group(1)), matcher.group(2).trim());
    }

    private String normalizeCppType(String type) {
        return type
                .replaceAll("(?m)\\b(public|private|protected)\\s*:\\s*", "")
                .replaceAll("\\s+", " ")
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

        for (CppParameter parameter : signature.parameters()) {
            if (!isSupportedCppParameterType(parameter.type())) {
                return false;
            }
        }

        return signature.parameters().size() <= 2;
    }

    private boolean isSupportedCppReturnType(String type) {
        return switch (type) {
            case "int", "string", "vector<int>", "ListNode*", "TreeNode*" -> true;
            default -> false;
        };
    }

    private boolean isSupportedCppParameterType(String type) {
        return switch (type) {
            case "int", "string", "const string&",
                    "vector<int>", "vector<int>&", "const vector<int>&",
                    "ListNode*", "TreeNode*" -> true;
            default -> false;
        };
    }

    private String buildCppSupportFunctions(CppFunctionSignature signature) {
        StringBuilder builder = new StringBuilder();
        boolean needsVectorInt = usesType(signature, "vector<int>")
                || usesType(signature, "vector<int>&")
                || usesType(signature, "const vector<int>&");
        boolean needsInt = usesType(signature, "int");
        boolean needsString = usesType(signature, "string")
                || usesType(signature, "const string&");
        boolean needsListNode = usesType(signature, "ListNode*");
        boolean needsTreeNode = usesType(signature, "TreeNode*");

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
                """);

        if (needsVectorInt || needsListNode) {
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

        if (needsInt) {
            builder.append("""

                    static int parseInt(string line) {
                        return stoi(trim(line));
                    }
                    """);
        }

        if (needsString) {
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

        if ("vector<int>".equals(signature.returnType())) {
            builder.append("""

                    static void printVectorInt(const vector<int>& values) {
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

    private String buildCppMain(CppFunctionSignature signature) {
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

        builder.append("\n    Solution solution;\n");
        builder.append("    auto result = solution.")
                .append(signature.functionName())
                .append("(")
                .append(String.join(", ", signature.parameters().stream().map(CppParameter::name).toList()))
                .append(");\n");
        builder.append(buildCppPrintStatement(signature.returnType()));
        builder.append("\n    return 0;\n");
        builder.append("}\n");
        return builder.toString();
    }

    private String buildCppParseExpression(String type, int index) {
        String source = "readLineOrDefault(lines, " + index + ")";
        return switch (type) {
            case "int" -> "parseInt(" + source + ")";
            case "string", "const string&" -> "parseStringValue(" + source + ")";
            case "vector<int>", "vector<int>&", "const vector<int>&" -> "parseVectorInt(" + source + ")";
            case "ListNode*" -> "parseListNode(" + source + ")";
            case "TreeNode*" -> "parseTreeNode(" + source + ")";
            default -> source;
        };
    }

    private String buildCppPrintStatement(String returnType) {
        return switch (returnType) {
            case "int", "string" -> "    cout << result;\n";
            case "vector<int>" -> "    printVectorInt(result);\n";
            case "ListNode*" -> "    printListNode(result);\n";
            case "TreeNode*" -> "    printTreeNode(result);\n";
            default -> "    // Unsupported return type for auto runner.\n";
        };
    }

    private String toCppStorageType(String type) {
        return switch (type) {
            case "vector<int>&", "const vector<int>&" -> "vector<int>";
            case "const string&" -> "string";
            default -> type;
        };
    }

    private boolean usesType(CppFunctionSignature signature, String type) {
        if (type.equals(signature.returnType())) {
            return true;
        }
        return signature.parameters().stream().anyMatch(parameter -> type.equals(parameter.type()));
    }

    private boolean usesListNode(CppFunctionSignature signature) {
        if ("ListNode*".equals(signature.returnType())) {
            return true;
        }
        return signature.parameters().stream().anyMatch(parameter -> "ListNode*".equals(parameter.type()));
    }

    private boolean usesTreeNode(CppFunctionSignature signature) {
        if ("TreeNode*".equals(signature.returnType())) {
            return true;
        }
        return signature.parameters().stream().anyMatch(parameter -> "TreeNode*".equals(parameter.type()));
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

    private record CppFunctionSignature(String returnType, String functionName, List<CppParameter> parameters) {
    }

    private record CppParameter(String type, String name) {
    }
}
