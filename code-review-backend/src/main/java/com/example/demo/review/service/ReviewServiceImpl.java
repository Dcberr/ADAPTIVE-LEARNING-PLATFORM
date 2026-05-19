package com.example.demo.review.service;

import java.time.Instant;
import java.util.*;

import org.springframework.stereotype.Service;

import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
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
import com.example.demo.user.entity.Role;
import com.example.demo.user.repository.UserRepository;
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
    private final UserRepository userRepository;

    private final ObjectMapper objectMapper;

    @Override
    public ReviewResponse reviewSubmission(UUID submissionId, UUID requesterId) {

        Submission submission =
                submissionRepository.findById(submissionId)
                        .orElseThrow();

        validateSubmissionReviewAccess(requesterId, submission);

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
                            "submission_id", prevSubmission.getId().toString(),
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

        saveReview(problem.getId(), submissionId, review, submission.getLanguage(), submission.getUserId());

        // review.setTestcaseResults(testcases);

        return review;
    }

    private void validateSubmissionReviewAccess(UUID requesterId, Submission submission) {
        var requester = userRepository.findById(requesterId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        boolean canAccess = requester.getId().equals(submission.getUserId())
                || requester.getRole() == Role.INSTRUCTOR
                || requester.getRole() == Role.ADMIN;

        if (!canAccess) {
            throw new AppException(ErrorCode.FORBIDDEN);
        }
    }

    private void saveReview(UUID problemId, UUID submissionId,
                            ReviewResponse review, String language, UUID userId) {

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
                            .problemId(problemId)
                            .language(language)
                            .userId(userId)
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
                .map(r -> deserializeReview(r.getReviewItemsJson()))
                .toList();
    }

    @Override
    public ReviewResponse reviewCode(UUID problemId, UUID submissionId, String code, String language, UUID userId) {
        Problem problem = problemRepository.findById(problemId)
                .orElseThrow();

        List<TestcaseResult> testcases =
                executionService.runByTestcase(RunTestcaseRequest.builder()
                                .problemId(problemId)
                                .language(language)
                                .code(code)
                                .build())
                        .getTestcases();

        log.info("Testcase results for direct review: {}", testcases);

        List<ReviewTestcaseResult> testcaseResults =
                testcases.stream()
                        .map(tc -> ReviewTestcaseResult.builder()
                                .testcaseId(tc.getTestcaseId())
                                .input(tc.getInput())
                                .expectedOutput(tc.getExpectedOutput())
                                .passed(tc.getStatus() == JudgeStatus.ACCEPTED)
                                .actualOutput(tc.getOutput())
                                .build())
                        .toList();

        // Build history from previous submissions and direct reviews
        List<Map<String, Object>> history = submissionRepository
                .findByProblemId(problemId)
                .stream()
                .filter(s -> s.getUserId().equals(userId))
                .sorted((a, b) -> b.getSubmittedAt().compareTo(a.getSubmittedAt()))
                .map(prevSubmission -> {
                    List<TestcaseResult> prevTestcases = executionService.runByTestcase(
                            RunTestcaseRequest.builder()
                                    .problemId(problemId)
                                    .language(prevSubmission.getLanguage())
                                    .code(prevSubmission.getCode())
                                    .build()
                    ).getTestcases();
                    
                    List<UUID> failedTestcaseIds = prevTestcases.stream()
                            .filter(tc -> tc.getStatus() != JudgeStatus.ACCEPTED)
                            .map(TestcaseResult::getTestcaseId)
                            .toList();
                    
                    return Map.of(
                            "submission_id", prevSubmission.getId().toString(),
                            "code", prevSubmission.getCode(),
                            "failed_test_case_ids", failedTestcaseIds
                    );
                })
                .toList();

        Map<String, Object> body = Map.of(
                "assignment", Map.of(
                        "content", problem.getDescription(),
                        "language", language
                ),
                "code", code,
                "test_results", testcaseResults.stream()
                        .map(tc -> Map.of(
                                "testcase_id", tc.getTestcaseId(),
                                "name", "Testcase " + tc.getInput(),
                                "input", tc.getInput(),
                                "expect", tc.getExpectedOutput(),
                                "actual", normalize(tc.getActualOutput())
                        ))
                        .toList(),
                "history", history
        );

        log.info("Review request body for direct code review: {}", body);

        ReviewResponse review = reviewAgentClient.reviewCode(body);

        // Save review to database
        saveDirectCodeReview(problemId, submissionId, code, language, review, userId);

        return review;
    }

    private void saveDirectCodeReview(UUID problemId, UUID submissionId, String code,
                                      String language, ReviewResponse review, UUID userId) {
        try {
            String reviewItemsJson = objectMapper.writeValueAsString(review);
            UUID matchedSubmissionId = resolveLinkedSubmissionId(problemId, submissionId, code, language, userId);

            CodeReview entity = CodeReview.builder()
                    .submissionId(matchedSubmissionId)
                    .problemId(problemId)
                    .language(language)
                    .summary(review.getSummary())
                    .detail(review.getDetail())
                    .reviewItemsJson(reviewItemsJson)
                    .createdAt(Instant.now())
                    .userId(userId)
                    .build();

            codeReviewRepository.save(entity);
        } catch (Exception e) {
            log.error("Failed to save direct code review", e);
        }
    }

    private UUID resolveLinkedSubmissionId(UUID problemId, UUID submissionId, String code, String language, UUID userId) {
        if (submissionId != null) {
            return resolveRequestedSubmissionId(problemId, submissionId, userId);
        }

        return submissionRepository.getAllSubmissionsByProblemIdAndUserId(userId, problemId).stream()
                .filter(submission -> submission.getSubmittedAt() != null)
                .filter(submission -> Objects.equals(submission.getLanguage(), language))
                .filter(submission -> Objects.equals(normalizeCode(submission.getCode()), normalizeCode(code)))
                .max(Comparator.comparing(
                                Submission::getSubmittedAt,
                                Comparator.nullsLast(Comparator.naturalOrder())
                        )
                        .thenComparing(
                                Submission::getId,
                                Comparator.nullsLast(Comparator.naturalOrder())
                        ))
                .map(Submission::getId)
                .orElse(null);
    }

    private UUID resolveRequestedSubmissionId(UUID problemId, UUID submissionId, UUID requesterId) {
        Submission submission = submissionRepository.findById(submissionId)
                .orElseThrow(() -> new AppException(ErrorCode.SUBMISSION_NOT_FOUND));

        validateSubmissionReviewAccess(requesterId, submission);

        if (!Objects.equals(submission.getProblemId(), problemId)) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        return submission.getId();
    }

    private String normalizeCode(String code) {
        if (code == null) {
            return "";
        }

        return Arrays.stream(code.replace("\r\n", "\n").replace('\r', '\n').split("\n", -1))
                .map(line -> line.replaceAll("\\s+$", ""))
                .collect(java.util.stream.Collectors.joining("\n"))
                .trim();
    }

    @Override
    public List<ReviewResponse> getProblemReviews(UUID problemId) {
        return codeReviewRepository.findByProblemId(problemId)
                .stream()
                .map(r -> deserializeReview(r.getReviewItemsJson()))
                .toList();
    }

    @Override
    public List<ReviewResponse> getSubmissionReviewsByUser(UUID submissionId, UUID userId) {
        Submission submission = submissionRepository.findById(submissionId)
                .orElseThrow();
        Instant submittedAt = submission.getSubmittedAt();
        Instant nextSubmissionAt = findNextSubmissionAt(submission);
        
        var userOpt = userRepository.findById(userId);
        if (userOpt.isEmpty()) {
            throw new IllegalArgumentException("User not found");
        }
        
        var user = userOpt.get();
        
        // Only allow if user is the submission owner or is an instructor/admin
        if (!submission.getUserId().equals(userId) && 
            !user.getRole().equals(Role.INSTRUCTOR) && 
            !user.getRole().equals(Role.ADMIN)) {
            throw new SecurityException("Unauthorized access");
        }

        return codeReviewRepository.findBySubmissionId(submissionId)
                .stream()
                .filter(review -> isOnOrAfter(review.getCreatedAt(), submittedAt))
                .filter(review -> isBeforeNextSubmission(review.getCreatedAt(), nextSubmissionAt))
                .sorted(Comparator.comparing(
                        CodeReview::getCreatedAt,
                        Comparator.nullsLast(Comparator.reverseOrder())
                ).thenComparing(
                        CodeReview::getId,
                        Comparator.nullsLast(Comparator.reverseOrder())
                ))
                .map(r -> deserializeReview(r.getReviewItemsJson()))
                .toList();
    }

    @Override
    public List<ReviewResponse> getProblemReviewsByUser(UUID problemId, UUID userId) {
        var userOpt = userRepository.findById(userId);
        if (userOpt.isEmpty()) {
            throw new IllegalArgumentException("User not found");
        }
        
        var user = userOpt.get();
        
        // Check if user is instructor or admin
        boolean isInstructor = user.getRole().equals(Role.INSTRUCTOR) || user.getRole().equals(Role.ADMIN);
        
        if (isInstructor) {
            // Instructors can see all reviews for a problem
            return codeReviewRepository.findByProblemId(problemId)
                    .stream()
                    .map(r -> deserializeReview(r.getReviewItemsJson()))
                    .toList();
        } else {
            // Students can only see their own direct code reviews (where userId = their userId and submissionId is null)
            return codeReviewRepository.findByProblemIdAndUserId(problemId, userId)
                    .stream()
                    .filter(r -> r.getSubmissionId() == null)  // Only direct reviews without submission
                    .map(r -> deserializeReview(r.getReviewItemsJson()))
                    .toList();
        }
    }

    @Override
    public List<ReviewResponse> getAllReviewsForUser(UUID userId) {
        var userOpt = userRepository.findById(userId);
        if (userOpt.isEmpty()) {
            throw new IllegalArgumentException("User not found");
        }
        
        var user = userOpt.get();
        
        // Only instructors and admins can view all reviews
        if (!user.getRole().equals(Role.INSTRUCTOR) && 
            !user.getRole().equals(Role.ADMIN)) {
            throw new SecurityException("Only instructors can view all reviews");
        }

        return codeReviewRepository.findAll()
                .stream()
                .map(r -> deserializeReview(r.getReviewItemsJson()))
                .toList();
    }

    private ReviewResponse deserializeReview(String reviewJsonString) {
        try {
            return objectMapper.readValue(reviewJsonString, ReviewResponse.class);
        } catch (Exception e) {
            log.error("Failed to deserialize review JSON", e);
            return ReviewResponse.builder()
                    .summary("Error parsing review")
                    .detail("Could not deserialize review data")
                    .build();
        }
    }

        private String normalize(String output) {
                return output == null ? "" : output.trim();
        }

        @Override
        public List<ReviewResponse> getReviewByUserIdAndProblemId(UUID userId, UUID problemId) {
            return codeReviewRepository.findByProblemIdAndUserId(problemId, userId)
                    .stream()
                    .map(r -> deserializeReview(r.getReviewItemsJson()))
                    .toList();
        }

        private Instant findNextSubmissionAt(Submission submission) {
            Instant submittedAt = submission.getSubmittedAt();

            return submissionRepository.getAllSubmissionsByProblemIdAndUserId(submission.getUserId(), submission.getProblemId())
                    .stream()
                    .filter(candidate -> !candidate.getId().equals(submission.getId()))
                    .map(Submission::getSubmittedAt)
                    .filter(candidateSubmittedAt -> candidateSubmittedAt != null && submittedAt != null)
                    .filter(candidateSubmittedAt -> candidateSubmittedAt.isAfter(submittedAt))
                    .min(Comparator.naturalOrder())
                    .orElse(null);
        }

        private boolean isOnOrAfter(Instant candidate, Instant reference) {
            if (candidate == null) {
                return false;
            }

            return reference == null || !candidate.isBefore(reference);
        }

        private boolean isBeforeNextSubmission(Instant candidate, Instant nextSubmissionAt) {
            return candidate != null && (nextSubmissionAt == null || candidate.isBefore(nextSubmissionAt));
        }

}
