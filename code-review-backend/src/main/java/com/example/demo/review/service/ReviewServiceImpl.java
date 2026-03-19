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
                                .input(tc.getInput())
                                .expectedOutput(tc.getExpectedOutput())
                                .passed(tc.getStatus() == JudgeStatus.ACCEPTED)
                                . actualOutput(tc.getOutput())
                                .build())
                        .toList();

        Map<String, Object> body = Map.of(
                "assignment", Map.of(
                        "content", problem.getTitle(),
                        "language", submission.getLanguage()
                ),
                "student_submission", Map.of(
                        "code", submission.getCode(),
                        "language", submission.getLanguage()
                ),
                "test_results", testcaseResults.stream()
                        .map(tc -> Map.of(
                                "name", tc.getInput(), 
                                "input", tc.getInput(),
                                "status", tc.isPassed() ? "PASSED" : "FAILED",
                                "expect", tc.getExpectedOutput(),
                                "actual", normalize(tc.getActualOutput())
                        ))
                        .toList()
        );

        ReviewResponse review =
                reviewAgentClient.reviewCode(body);

        saveReview(submissionId, review);

        review.setTestcaseResults(testcases);

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