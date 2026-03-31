package com.example.demo.execution.service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.springframework.stereotype.Service;

import com.example.demo.execution.client.JobeClient;
import com.example.demo.execution.dto.ExecutionResult;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.model.JudgeUtil;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.TestcaseRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExecutionServiceImpl implements ExecutionService {

    private final JobeClient jobeClient;
    private final TestcaseRepository testcaseRepository;

    private final ExecutorService executor =
            Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

    @Override
    public RunCodeResponse runByTestcase(RunTestcaseRequest request) {

        List<Testcase> testcases =
                testcaseRepository.findByProblemId(request.getProblemId());

        // ===== COMPILE ONCE =====
        ExecutionResult compileResult =
                jobeClient.compile(request.getLanguage(), request.getCode());

        JudgeStatus compileStatus = mapOutcome(compileResult);

        if (compileStatus == JudgeStatus.COMPILE_ERROR) {

            TestcaseResult compileError =
                    TestcaseResult.builder()
                            .index(1)
                            .error(compileResult.getStderr())
                            .status(JudgeStatus.COMPILE_ERROR)
                            .runtime(compileResult.getRuntime())
                            .build();

            return RunCodeResponse.builder()
                    .status(JudgeStatus.COMPILE_ERROR)
                    .testcases(List.of(compileError))
                    .passedTestcases(0)
                    .totalTestcases(testcases.size())
                    .build();
        }

        // ===== RUN TESTCASES PARALLEL =====
        List<CompletableFuture<TestcaseResult>> futures = new ArrayList<>();

        int index = 1;

        for (Testcase tc : testcases) {

            int testcaseIndex = index++;

            futures.add(
                    CompletableFuture.supplyAsync(
                            () -> runSingleTestcase(testcaseIndex, request, tc),
                            executor
                    )
            );
        }

        List<TestcaseResult> results =
                futures.stream()
                        .map(CompletableFuture::join)
                        .toList();

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
                .build();
    }

    private TestcaseResult runSingleTestcase(
            int index,
            RunTestcaseRequest request,
            Testcase tc
    ) {

        ExecutionResult result =
                jobeClient.runCode(
                        request.getLanguage(),
                        request.getCode(),
                        tc.getInput()
                );

        JudgeStatus status = mapOutcome(result);

        String output = result.getStdout();
        String error = result.getStderr();
        log.info("Testcase #{}: status={}, output=[{}], error=[{}]", index, status, output, error);

        if (status == JudgeStatus.ACCEPTED) {

            boolean correct =
                    JudgeUtil.compareOutput(
                            tc.getExpectedOutput(),
                            output
                    );

            status = correct
                    ? JudgeStatus.ACCEPTED
                    : JudgeStatus.WRONG_ANSWER;
        }

        return TestcaseResult.builder()
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
}