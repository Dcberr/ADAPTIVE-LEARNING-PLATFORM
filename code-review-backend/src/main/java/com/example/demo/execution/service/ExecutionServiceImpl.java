package com.example.demo.execution.service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.stereotype.Service;

import com.example.demo.execution.client.JobeClient;
import com.example.demo.execution.dto.ExecutionResult;
import com.example.demo.execution.dto.RunCodeRequest;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.model.JudgeUtil;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.utils.CodeExtractor;
import com.example.demo.problem.utils.LeetCodeStarterCodeGenerator;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExecutionServiceImpl implements ExecutionService {

        private final JobeClient jobeClient;
        private final TestcaseRepository testcaseRepository;
        private final ProblemRepository problemRepository;
        private final LeetCodeStarterCodeGenerator leetCodeStarterCodeGenerator;

        private final ExecutorService executor = Executors
                        .newFixedThreadPool(Runtime.getRuntime().availableProcessors());

        private static final String CPP_UNSAFE_INT_READ = "int n; cin >> n;";
        private static final String CPP_SIGN_COMPARE_PRAGMA = "#pragma GCC diagnostic ignored \"-Wsign-compare\"";
        private static final Pattern CPP_MAIN_INPUT_LOOP_PATTERN = Pattern
                        .compile("for \\(size_t i = 0; i < (\\d+); \\+\\+i\\)");
        private static final String CPP_BITS_STDC = "#include <bits/stdc++.h>";
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
        private static final String CPP_SAFE_INT_READ = """
                        int n = 0;
                            if (!(cin >> n)) {
                                cerr << "Invalid input";
                                return 0;
                            }
                        """;

        @Override
        public RunCodeResponse runByTestcase(RunTestcaseRequest request) {

                List<Testcase> testcases = testcaseRepository.findByProblemId(request.getProblemId());

                // ===== LOAD PROBLEM AND COMBINE STARTER CODE WITH STUDENT CODE =====
                Problem problem = problemRepository.findById(request.getProblemId())
                                .orElseThrow(() -> new RuntimeException("Problem not found"));

                String template = getTemplate(problem, request.getLanguage());
                String combinedCode = CodeExtractor.combineWithStudentCode(template, request.getCode());
                String hardenedCode = hardenGeneratedCode(request.getLanguage(), combinedCode);
                log.info(
                                "Prepared combined code | problemId={} | language={} | source={}",
                                request.getProblemId(),
                                request.getLanguage(),
                                quoteForLog(hardenedCode));

                // ===== RUN TESTCASES PARALLEL =====
                List<CompletableFuture<TestcaseResult>> futures = new ArrayList<>();

                int index = 1;

                Long totalRuntimeStart = System.currentTimeMillis();
                for (Testcase tc : testcases) {

                        int testcaseIndex = index++;

                        futures.add(
                                        CompletableFuture.supplyAsync(
                                                        () -> runSingleTestcase(testcaseIndex, request, hardenedCode,
                                                                        tc),
                                                        executor));
                }

                List<TestcaseResult> results = futures.stream()
                                .map(CompletableFuture::join)
                                .toList();

                Long totalRuntime = System.currentTimeMillis() - totalRuntimeStart;
                log.info("Total runtime for all testcases: {} ms", totalRuntime);

                int passed = (int) results.stream()
                                .filter(r -> r.getStatus() == JudgeStatus.ACCEPTED)
                                .count();

                JudgeStatus finalStatus = results.stream()
                                .map(TestcaseResult::getStatus)
                                .filter(s -> s != JudgeStatus.ACCEPTED)
                                .findFirst()
                                .orElse(JudgeStatus.ACCEPTED);

                return RunCodeResponse.builder()
.status(finalStatus)
                                .testcases(results)
                                .passedTestcases(passed)
                                .totalTestcases(testcases.size())
                                .runtime(totalRuntime)
                                .build();
        }

        private TestcaseResult runSingleTestcase(
                        int index,
                        RunTestcaseRequest request,
                        String combinedCode,
                        Testcase tc) {

                String testcaseInputError = validateGeneratedInput(request.getLanguage(), combinedCode,
                                tc.getInput());
                if (testcaseInputError != null) {
                        log.warn(
                                        "Skipped testcase run due to invalid generated input | testcaseIndex={} | testcaseId={} | error={}",
                                        index,
                                        tc.getId(),
                                        testcaseInputError);

                        return TestcaseResult.builder()
                                        .testcaseId(tc.getId())
                                        .index(index)
                                        .input(tc.getInput())
                                        .expectedOutput(tc.getExpectedOutput())
                                        .output("")
                                        .error(testcaseInputError)
                                        .runtime(0L)
                                        .status(JudgeStatus.RUNTIME_ERROR)
                                        .build();
                }

                ExecutionResult result = jobeClient.runCode(
                                request.getLanguage(),
                                combinedCode,
                                tc.getInput());

                JudgeStatus status = mapOutcome(result);

                String output = result.getStdout();
                String error = result.getStderr();
                log.info(
                                "Raw testcase result | testcaseIndex={} | testcaseId={} | input={} | expected={} | output={} | error={} | mappedStatus={}",
                                index,
                                tc.getId(),
                                quoteForLog(tc.getInput()),
                                quoteForLog(tc.getExpectedOutput()),
                                quoteForLog(output),
                                quoteForLog(error),
                                status);

                if (status == JudgeStatus.ACCEPTED) {

                        boolean correct = JudgeUtil.compareOutput(
                                        tc.getExpectedOutput(),
                                        output);

                        status = correct
                                        ? JudgeStatus.ACCEPTED
: JudgeStatus.WRONG_ANSWER;

                        log.info(
                                        "Compared testcase result | testcaseIndex={} | testcaseId={} | finalStatus={}",
                                        index,
                                        tc.getId(),
                                        status);
                }

                return TestcaseResult.builder()
                                .testcaseId(tc.getId())
                                .index(index)
                                .input(tc.getInput())
                                .expectedOutput(tc.getExpectedOutput())
                                .output(output)
                                .error(error)
                                .runtime(result.getRuntime())
                                .status(status)
                                .build();
        }

        private JudgeStatus mapOutcome(ExecutionResult result) {

                int outcome = result.getExitCode();

                return switch (outcome) {

                        case 15 -> JudgeStatus.ACCEPTED;

                        case 11 -> JudgeStatus.COMPILE_ERROR;

                        case 12 -> JudgeStatus.RUNTIME_ERROR;

                        case 13 -> JudgeStatus.TIME_LIMIT;

                        default -> JudgeStatus.RUNTIME_ERROR;
                };
        }

        /**
         * Get template from problem
         */
        private String getTemplate(Problem problem, String language) {
                if (problem.getStarterCodes() != null &&
                                problem.getStarterCodes().containsKey(language)) {
                        String template = problem.getStarterCodes().get(language);
                        if ("cpp".equalsIgnoreCase(language)) {
                                template = repairCppTemplate(template);
                        }
                        return template;
                }

                throw new RuntimeException("No starter code template found for language: " + language);
        }

        /**
         * Repairs stale C++ templates stored in the database:
         * 1. If the template is a bare class without main(), regenerate it fully using
         * LeetCodeStarterCodeGenerator so that includes, support functions, and main()
         * are added.
         * 2. Fixes the old parseVectorInt omission bug where vector<int> parameters
         * were assigned
         * directly from readLineOrDefault() without parsing.
         */
        private String repairCppTemplate(String template) {
                if (template == null) {
                        return null;
                }

                template = normalizeCppIncludes(template);

                // If the template lacks a main() function it is a bare class skeleton stored
                // before
                // full template generation was implemented. Regenerate it so the code is
                // runnable.
if (!template.contains("int main(")) {
                        log.info("C++ template missing main() — regenerating full runnable template");
                        template = leetCodeStarterCodeGenerator.generateCppTemplatePublic(template);
                }

                // Fix old bug: vector<int> param assigned from readLineOrDefault() without
                // parseVectorInt()
                template = template.replaceAll(
                                "(vector<int>\\s+\\w+\\s*=\\s*)(readLineOrDefault\\([^)]+\\))(;)",
                                "$1parseVectorInt($2)$3");

                return template;
        }

        private String normalizeCppIncludes(String template) {
                if (template.contains(CPP_BITS_STDC)) {
                        return template.replace(CPP_BITS_STDC, CPP_DEFAULT_INCLUDES.stripTrailing());
                }
                return template;
        }

        @Override
        public RunCodeResponse runByCustomInput(RunCodeRequest request) {
                ExecutionResult result = jobeClient.runCode(
                                request.getLanguage(),
                                request.getCode(),
                                request.getInput());

                JudgeStatus status = mapOutcome(result);

                return RunCodeResponse.builder()
                                .status(status)
                                .testcases(List.of(
                                                TestcaseResult.builder()
                                                                .index(1)
                                                                .input(request.getInput())
                                                                .output(result.getStdout())
                                                                .error(result.getStderr())
                                                                .runtime(result.getRuntime())
                                                                .status(status)
                                                                .build()))
                                .passedTestcases(status == JudgeStatus.ACCEPTED ? 1 : 0)
                                .totalTestcases(1)
                                .build();
        }

        private String quoteForLog(String value) {
                if (value == null) {
                        return "<null>";
                }

                String escaped = value
                                .replace("\\", "\\\\")
                                .replace("\r", "\\r")
                                .replace("\n", "\\n")
                                .replace("\t", "\\t");

                if (escaped.length() > 1200) {
                        return "\"" + escaped.substring(0, 1200) + "...(truncated)\"";
                }

                return "\"" + escaped + "\"";
        }
private String hardenGeneratedCode(String language, String combinedCode) {
                if (!"cpp".equalsIgnoreCase(language) || combinedCode == null || combinedCode.isBlank()) {
                        return combinedCode;
                }

                String hardenedCode = applyCppWarningGuards(combinedCode);

                if (hardenedCode.contains(CPP_UNSAFE_INT_READ)) {
                        hardenedCode = hardenedCode.replace(CPP_UNSAFE_INT_READ, CPP_SAFE_INT_READ);
                        log.info("Applied C++ input hardening for common 'int n; cin >> n;' main pattern");
                }

                return hardenedCode;
        }

        private String validateGeneratedInput(String language, String combinedCode, String input) {
                if (!"cpp".equalsIgnoreCase(language) || combinedCode == null || combinedCode.isBlank()) {
                        return null;
                }

                Integer expectedLines = extractCppExpectedInputLineCount(combinedCode);
                if (expectedLines == null || expectedLines <= 1) {
                        return null;
                }

                int actualLines = countInputLines(input);
                if (actualLines >= expectedLines) {
                        return null;
                }

                return "Invalid testcase input format for generated C++ template: expected "
                                + expectedLines
                                + " line(s) for function arguments, but received "
                                + actualLines
                                + ". Use one argument per line, for example: [2,7,11,15]\\n9";
        }

        private Integer extractCppExpectedInputLineCount(String combinedCode) {
                Matcher matcher = CPP_MAIN_INPUT_LOOP_PATTERN.matcher(combinedCode);
                if (!matcher.find()) {
                        return null;
                }

                return Integer.parseInt(matcher.group(1));
        }

        private int countInputLines(String input) {
                if (input == null || input.isBlank()) {
                        return 0;
                }

                return input.split("\\r?\\n", -1).length;
        }

        private String applyCppWarningGuards(String source) {
                if (source.contains(CPP_SIGN_COMPARE_PRAGMA)) {
                        return source;
                }

                int lastIncludeIndex = source.lastIndexOf("#include ");
                if (lastIncludeIndex == -1) {
                        log.info("Applied C++ warning guard pragma for -Wsign-compare");
                        return CPP_SIGN_COMPARE_PRAGMA + "\n" + source;
                }

                int insertionPoint = source.indexOf('\n', lastIncludeIndex);
                if (insertionPoint == -1) {
                        log.info("Applied C++ warning guard pragma for -Wsign-compare");
return source + "\n" + CPP_SIGN_COMPARE_PRAGMA + "\n";
                }

                String withPragma = source.substring(0, insertionPoint + 1)
                                + CPP_SIGN_COMPARE_PRAGMA
                                + "\n"
                                + source.substring(insertionPoint + 1);
                log.info("Applied C++ warning guard pragma for -Wsign-compare");
                return withPragma;
        }
}