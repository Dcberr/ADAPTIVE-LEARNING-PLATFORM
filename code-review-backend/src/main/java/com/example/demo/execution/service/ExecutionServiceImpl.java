package com.example.demo.execution.service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

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

    private final ExecutorService executor =
            Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

    private static final String CPP_UNSAFE_INT_READ = "int n; cin >> n;";
    private static final String CPP_SAFE_INT_READ = """
            int n = 0;
                if (!(cin >> n)) {
                    cerr << "Invalid input";
                    return 0;
                }
            """;

    @Override
    public RunCodeResponse runByTestcase(RunTestcaseRequest request) {

        List<Testcase> testcases =
                testcaseRepository.findByProblemId(request.getProblemId());

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
                quoteForLog(hardenedCode)
        );

        // ===== RUN TESTCASES PARALLEL =====
        List<CompletableFuture<TestcaseResult>> futures = new ArrayList<>();

        int index = 1;

        Long totalRuntimeStart = System.currentTimeMillis();
        for (Testcase tc : testcases) {

            int testcaseIndex = index++;

            futures.add(
                    CompletableFuture.supplyAsync(
                            () -> runSingleTestcase(testcaseIndex, request, hardenedCode, tc),
                            executor
                    )
            );
        }
        

        List<TestcaseResult> results =
                futures.stream()
                        .map(CompletableFuture::join)
                        .toList();

        Long totalRuntime = System.currentTimeMillis() - totalRuntimeStart;
        log.info("Total runtime for all testcases: {} ms", totalRuntime);

        int passed =
                (int) results.stream()
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
            Testcase tc
    ) {

        ExecutionResult result =
                jobeClient.runCode(
                        request.getLanguage(),
                        combinedCode,
                        tc.getInput()
                );

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
                status
        );

        if (status == JudgeStatus.ACCEPTED) {

            boolean correct =
                    JudgeUtil.compareOutput(
                            tc.getExpectedOutput(),
                            output
                    );

            status = correct
                    ? JudgeStatus.ACCEPTED
                    : JudgeStatus.WRONG_ANSWER;

            log.info(
                    "Compared testcase result | testcaseIndex={} | testcaseId={} | finalStatus={}",
                    index,
                    tc.getId(),
                    status
            );
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
     *    LeetCodeStarterCodeGenerator so that includes, support functions, and main() are added.
     * 2. Fixes the old parseVectorInt omission bug where vector<int> parameters were assigned
     *    directly from readLineOrDefault() without parsing.
     */
    private String repairCppTemplate(String template) {
        if (template == null) {
            return null;
        }


        // If the template lacks a main() function it is a bare class skeleton stored before
        // full template generation was implemented. Regenerate it so the code is runnable.
        if (!template.contains("int main(")) {
            log.info("C++ template missing main() — regenerating full runnable template");
            template = leetCodeStarterCodeGenerator.generateCppTemplatePublic(template);
        }


        // Fix old bug: vector<int> param assigned from readLineOrDefault() without parseVectorInt()
        template = template.replaceAll(
            "(vector<int>\\s+\\w+\\s*=\\s*)(readLineOrDefault\\([^)]+\\))(;)",
            "$1parseVectorInt($2)$3"
        );


        return template;
    }


    @Override
    public RunCodeResponse runByCustomInput(RunCodeRequest request) {
        ExecutionResult result =
                jobeClient.runCode(
                        request.getLanguage(),
                        request.getCode(),
                        request.getInput()
                );

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
                                .build()
                ))
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

        if (combinedCode.contains(CPP_UNSAFE_INT_READ)) {
            String hardenedCode = combinedCode.replace(CPP_UNSAFE_INT_READ, CPP_SAFE_INT_READ);
            log.info("Applied C++ input hardening for common 'int n; cin >> n;' main pattern");
            return hardenedCode;
        }

        return combinedCode;
    }
}
