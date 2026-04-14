package com.example.demo.review.service;

import java.time.Instant;
import java.util.*;

import org.springframework.stereotype.Service;

import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.review.client.ReviewAgentClient;
import com.example.demo.review.dto.*;
import com.example.demo.review.entity.CodeReview;
import com.example.demo.review.repository.CodeReviewRepository;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.repository.SubmissionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class ReviewServiceImpl implements ReviewService {

    private final SubmissionRepository submissionRepository;
    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;

    private final ExecutionService executionService;
    private final ReviewAgentClient reviewAgentClient;

    private final CodeReviewRepository codeReviewRepository;

    private final ObjectMapper objectMapper;

    @Override
    public ReviewResponse reviewSubmission(UUID submissionId) {

        Submission submission =
                submissionRepository.findById(submissionId)
                        .orElseThrow();

        Problem problem =
                problemRepository.findById(submission.getProblemId())
                        .orElseThrow();

        // List<Testcase> testcases =
        //         testcaseRepository.findByProblemId(problem.getId());

        List<TestcaseResult> testcases =
                executionService.runByTestcase(RunTestcaseRequest.builder()
                                .problemId(problem.getId())
                                .language(submission.getLanguage())
                                .code(submission.getCode())
                                .build())
                        .getTestcases();

        log.info("Testcase results: {}", testcases);
        // RunTestcaseRequest judgeRequest =
        //         new RunTestcaseRequest();

        // judgeRequest.setProblemId(problem.getId());
        // judgeRequest.setLanguage(submission.getLanguage());
        // judgeRequest.setCode(submission.getCode());

        // RunCodeResponse judgeResult =
        //         executionService.runByTestcase(judgeRequest);

        List<ReviewTestcaseResult> testcaseResults =
                testcases.stream()
                        .map(tc -> ReviewTestcaseResult.builder()
                                .testcaseId(tc.getTestcaseId())
                                .input(tc.getInput())
                                .expectedOutput(tc.getExpectedOutput())
                                .passed(tc.getStatus() == JudgeStatus.ACCEPTED)
                                . actualOutput(tc.getOutput())
                                .build())
                        .toList();

        log.info("Review testcase results 2: {}", testcaseResults);
        log.info("Problem title: {}", problem.getTitle());
        log.info("Submission language: {}", submission.getLanguage());
        log.info("Submission code: {}", submission.getCode());
        log.info("Normalized actual output: {}", testcaseResults.get(0).getActualOutput());
        log.info("Normalized expected output: {}", testcaseResults.get(0).getExpectedOutput());
        log.info("Normalized passed status: {}", testcaseResults.get(0).isPassed());
        log.info("Normalized input: {}", testcaseResults.get(0).getInput());
        log.info("Normalized testcase result: {}", testcaseResults.get(0));
        // Build history from previous submissions
        List<Map<String, Object>> history = submissionRepository
                .findByProblemIdAndIdNot(problem.getId(), submissionId)
                .stream()
                .sorted((a, b) -> b.getSubmittedAt().compareTo(a.getSubmittedAt()))
                .map(prevSubmission -> {
                    List<TestcaseResult> prevTestcases = executionService.runByTestcase(
                            RunTestcaseRequest.builder()
                                    .problemId(problem.getId())
                                    .language(prevSubmission.getLanguage())
                                    .code(prevSubmission.getCode())
                                    .build()
                    ).getTestcases();
                    
                    List<UUID> failedTestcaseIds = prevTestcases.stream()
                            .filter(tc -> tc.getStatus() != JudgeStatus.ACCEPTED)
                            .map(TestcaseResult::getTestcaseId)
                            .toList();
                    
                    return Map.of(
                            "code", prevSubmission.getCode(),
                            "failed_test_case_ids", failedTestcaseIds
                    );
                })
                .toList();

        Map<String, Object> body = Map.of(
                "assignment", Map.of(
                        "content", problem.getDescription(),
                        "language", submission.getLanguage()
                ),
                // "student_submission", Map.of(
                //         "code", submission.getCode()
                // ),
                "code", submission.getCode(),
                "test_results", testcaseResults.stream()
                        .map(tc -> Map.of(
                                "testcase_id", tc.getTestcaseId(),
                                "name", "Testcase " + tc.getInput(), 
                                "input", tc.getInput(),
                                // "status", tc.isPassed() ? "PASSED" : "FAILED",
                                "expect", tc.getExpectedOutput(),
                                "actual", normalize(tc.getActualOutput())
                        ))
                        .toList(),
                "history", history
        );

        log.info("Body send to review agent: {}", body);

        ReviewResponse review =
                reviewAgentClient.reviewCode(body);

        saveReview(submissionId, review);

        // review.setTestcaseResults(testcases);

        return review;
    }

    private void saveReview(UUID submissionId,
                            ReviewResponse review) {

        try {

            String reviewItemsJson =
                    objectMapper.writeValueAsString(review);

            CodeReview entity =
                    CodeReview.builder()
                            .submissionId(submissionId)
                            .summary(review.getSummary())
                            .detail(review.getDetail())
                            .reviewItemsJson(reviewItemsJson)
                            .createdAt(Instant.now())
                            .build();

            codeReviewRepository.save(entity);

        } catch (Exception e) {

            log.error("Failed to save review", e);
        }
    }

    @Override
    public List<ReviewResponse> getSubmissionReviews(UUID submissionId) {

        return codeReviewRepository.findBySubmissionId(submissionId)
                .stream()
                .map(r -> ReviewResponse.builder()
                        .summary(r.getSummary())
                        .detail(r.getDetail())
                        .build())
                .toList();
    }

    private String normalize(String output) {
        return output == null ? "" : output.trim();
}
}