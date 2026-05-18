package com.example.demo.review.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.review.client.ReviewAgentClient;
import com.example.demo.review.dto.ReviewResponse;
import com.example.demo.review.entity.CodeReview;
import com.example.demo.review.repository.CodeReviewRepository;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.repository.SubmissionRepository;
import com.example.demo.user.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

class ReviewServiceImplTest {

    private final SubmissionRepository submissionRepository = org.mockito.Mockito.mock(SubmissionRepository.class);
    private final ProblemRepository problemRepository = org.mockito.Mockito.mock(ProblemRepository.class);
    private final TestcaseRepository testcaseRepository = org.mockito.Mockito.mock(TestcaseRepository.class);
    private final ExecutionService executionService = org.mockito.Mockito.mock(ExecutionService.class);
    private final ReviewAgentClient reviewAgentClient = org.mockito.Mockito.mock(ReviewAgentClient.class);
    private final CodeReviewRepository codeReviewRepository = org.mockito.Mockito.mock(CodeReviewRepository.class);
    private final UserRepository userRepository = org.mockito.Mockito.mock(UserRepository.class);

    private final ReviewServiceImpl reviewService = new ReviewServiceImpl(
            submissionRepository,
            problemRepository,
            testcaseRepository,
            executionService,
            reviewAgentClient,
            codeReviewRepository,
            userRepository,
            new ObjectMapper());

    @Test
    @DisplayName("Should attach direct review to matching submitted submission")
    void shouldAttachDirectReviewToMatchingSubmittedSubmission() {
        UUID userId = UUID.randomUUID();
        UUID problemId = UUID.randomUUID();
        UUID submissionId = UUID.randomUUID();
        String code = "print('hello')";
        String language = "python";

        Problem problem = Problem.builder()
                .id(problemId)
                .description("Problem")
                .build();

        Submission matchingSubmission = Submission.builder()
                .id(submissionId)
                .userId(userId)
                .problemId(problemId)
                .language(language)
                .code(code)
                .submittedAt(Instant.parse("2026-05-19T10:00:00Z"))
                .build();

        RunCodeResponse runCodeResponse = RunCodeResponse.builder()
                .status(JudgeStatus.ACCEPTED)
                .passedTestcases(1)
                .totalTestcases(1)
                .testcases(List.<TestcaseResult>of())
                .build();

        ReviewResponse reviewResponse = ReviewResponse.builder()
                .summary("Looks good")
                .detail("Nice work")
                .build();

        when(problemRepository.findById(problemId)).thenReturn(Optional.of(problem));
        when(executionService.runByTestcase(any())).thenReturn(runCodeResponse);
        when(reviewAgentClient.reviewCode(any())).thenReturn(reviewResponse);
        when(submissionRepository.findByProblemId(problemId)).thenReturn(List.of(matchingSubmission));
        when(submissionRepository.getAllSubmissionsByProblemIdAndUserId(userId, problemId))
                .thenReturn(List.of(matchingSubmission));

        reviewService.reviewCode(problemId, null, code, language, userId);

        ArgumentCaptor<CodeReview> reviewCaptor = ArgumentCaptor.forClass(CodeReview.class);
        verify(codeReviewRepository).save(reviewCaptor.capture());
        assertEquals(submissionId, reviewCaptor.getValue().getSubmissionId());
    }

    @Test
    @DisplayName("Should keep direct review detached when code does not match a submitted submission")
    void shouldKeepDirectReviewDetachedWhenCodeDoesNotMatchSubmittedSubmission() {
        UUID userId = UUID.randomUUID();
        UUID problemId = UUID.randomUUID();
        String submittedCode = "print('old')";
        String reviewingCode = "print('new')";
        String language = "python";

        Problem problem = Problem.builder()
                .id(problemId)
                .description("Problem")
                .build();

        Submission previousSubmission = Submission.builder()
                .id(UUID.randomUUID())
                .userId(userId)
                .problemId(problemId)
                .language(language)
                .code(submittedCode)
                .submittedAt(Instant.parse("2026-05-19T10:00:00Z"))
                .build();

        RunCodeResponse runCodeResponse = RunCodeResponse.builder()
                .status(JudgeStatus.ACCEPTED)
                .passedTestcases(1)
                .totalTestcases(1)
                .testcases(List.<TestcaseResult>of())
                .build();

        ReviewResponse reviewResponse = ReviewResponse.builder()
                .summary("Looks good")
                .detail("Nice work")
                .build();

        when(problemRepository.findById(problemId)).thenReturn(Optional.of(problem));
        when(executionService.runByTestcase(any())).thenReturn(runCodeResponse);
        when(reviewAgentClient.reviewCode(any())).thenReturn(reviewResponse);
        when(submissionRepository.findByProblemId(problemId)).thenReturn(List.of(previousSubmission));
        when(submissionRepository.getAllSubmissionsByProblemIdAndUserId(userId, problemId))
                .thenReturn(List.of(previousSubmission));

        reviewService.reviewCode(problemId, null, reviewingCode, language, userId);

        ArgumentCaptor<CodeReview> reviewCaptor = ArgumentCaptor.forClass(CodeReview.class);
        verify(codeReviewRepository).save(reviewCaptor.capture());
        assertNull(reviewCaptor.getValue().getSubmissionId());
    }

    @Test
    @DisplayName("Should attach direct review when submission ID is provided explicitly")
    void shouldAttachDirectReviewWithExplicitSubmissionId() {
        UUID requesterId = UUID.randomUUID();
        UUID submissionId = UUID.randomUUID();
        UUID problemId = UUID.randomUUID();
        String language = "python";
        String submittedCode = "print('hello')\n";

        Problem problem = Problem.builder()
                .id(problemId)
                .description("Problem")
                .build();

        Submission submission = Submission.builder()
                .id(submissionId)
                .userId(requesterId)
                .problemId(problemId)
                .language(language)
                .code(submittedCode)
                .submittedAt(Instant.parse("2026-05-19T10:00:00Z"))
                .build();

        var user = com.example.demo.user.entity.User.builder()
                .id(requesterId)
                .role(com.example.demo.user.entity.Role.STUDENT)
                .build();

        RunCodeResponse runCodeResponse = RunCodeResponse.builder()
                .status(JudgeStatus.ACCEPTED)
                .passedTestcases(1)
                .totalTestcases(1)
                .testcases(List.<TestcaseResult>of())
                .build();

        ReviewResponse reviewResponse = ReviewResponse.builder()
                .summary("Looks good")
                .detail("Nice work")
                .build();

        when(problemRepository.findById(problemId)).thenReturn(Optional.of(problem));
        when(submissionRepository.findById(submissionId)).thenReturn(Optional.of(submission));
        when(userRepository.findById(requesterId)).thenReturn(Optional.of(user));
        when(executionService.runByTestcase(any())).thenReturn(runCodeResponse);
        when(reviewAgentClient.reviewCode(any())).thenReturn(reviewResponse);
        when(submissionRepository.findByProblemId(problemId)).thenReturn(List.of(submission));

        reviewService.reviewCode(problemId, submissionId, submittedCode, language, requesterId);

        ArgumentCaptor<CodeReview> reviewCaptor = ArgumentCaptor.forClass(CodeReview.class);
        verify(codeReviewRepository).save(reviewCaptor.capture());
        assertEquals(submissionId, reviewCaptor.getValue().getSubmissionId());
    }
}
