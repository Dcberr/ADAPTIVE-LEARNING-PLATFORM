package com.example.demo.submission.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import com.example.demo.assignment.dto.UpdateAssignmentRequest;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.assignment.service.AssignmentService;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.execution.model.JudgeStatus;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.recommendation.repository.RecommendationHistoryRepository;
import com.example.demo.review.repository.CodeReviewRepository;
import com.example.demo.submission.dto.SubmissionResponse;
import com.example.demo.submission.dto.SubmitCodeRequest;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.entity.SubmissionStatus;
import com.example.demo.submission.repository.SubmissionRepository;

class SubmissionServiceImplTest {

    private final SubmissionRepository submissionRepository = org.mockito.Mockito.mock(SubmissionRepository.class);
    private final ExecutionService executionService = org.mockito.Mockito.mock(ExecutionService.class);
    private final AssignmentService assignmentService = org.mockito.Mockito.mock(AssignmentService.class);
    private final AssignmentProblemRepository assignmentProblemRepository = org.mockito.Mockito
            .mock(AssignmentProblemRepository.class);
    private final AssignmentRepository assignmentRepository = org.mockito.Mockito.mock(AssignmentRepository.class);
    private final ProblemRepository problemRepository = org.mockito.Mockito.mock(ProblemRepository.class);
    private final CodeReviewRepository codeReviewRepository = org.mockito.Mockito.mock(CodeReviewRepository.class);
    private final RecommendationHistoryRepository recommendationHistoryRepository = org.mockito.Mockito
            .mock(RecommendationHistoryRepository.class);

    private final SubmissionServiceImpl submissionService = new SubmissionServiceImpl(
            submissionRepository,
            executionService,
            assignmentService,
            assignmentProblemRepository,
            assignmentRepository,
            problemRepository,
            codeReviewRepository,
            recommendationHistoryRepository);

    @Test
    @DisplayName("Should allow library problem submission without assignment mapping")
    void shouldAllowLibraryProblemSubmissionWithoutAssignmentMapping() {
        UUID userId = UUID.randomUUID();
        UUID problemId = UUID.randomUUID();
        Instant startedAt = Instant.now();

        SubmitCodeRequest request = new SubmitCodeRequest();
        request.setProblemId(problemId);
        request.setLanguage("java");
        request.setCode("class Solution {}");
        request.setStartedAt(startedAt);

        Problem libraryProblem = Problem.builder()
                .id(problemId)
                .type(ProblemType.LIBRARY)
                .build();

        RunCodeResponse runCodeResponse = RunCodeResponse.builder()
                .status(JudgeStatus.ACCEPTED)
                .runtime(12L)
                .passedTestcases(2)
                .totalTestcases(2)
                .testcases(List.<TestcaseResult>of())
                .build();

        Submission savedSubmission = Submission.builder()
                .id(UUID.randomUUID())
                .submittedAt(Instant.now())
                .score("100.0")
                .build();

        when(problemRepository.findByIdAndDeletedAtIsNull(problemId)).thenReturn(Optional.of(libraryProblem));
        when(executionService.runByTestcase(any())).thenReturn(runCodeResponse);
        when(submissionRepository.save(any(Submission.class))).thenReturn(savedSubmission);

        SubmissionResponse response = submissionService.submit(userId, request);

        assertEquals(savedSubmission.getId(), response.getSubmissionId());
        assertEquals(savedSubmission.getScore(), response.getScore());
        verify(assignmentProblemRepository, never()).findByProblemId(problemId);
        verify(assignmentRepository, never()).findByIdAndDeletedAtIsNull(any());
        verify(submissionRepository, never()).countByUserIdAndAssignmentId(any(), any());
        verify(assignmentService, never()).updateAssignment(any(), any(UpdateAssignmentRequest.class));

        ArgumentCaptor<Submission> submissionCaptor = ArgumentCaptor.forClass(Submission.class);
        verify(submissionRepository).save(submissionCaptor.capture());
        assertEquals(userId, submissionCaptor.getValue().getUserId());
        assertEquals(problemId, submissionCaptor.getValue().getProblemId());
    }

    @Test
    @DisplayName("Should enforce assignment submission rules for class problems")
    void shouldEnforceAssignmentSubmissionRulesForClassProblems() {
        UUID userId = UUID.randomUUID();
        UUID problemId = UUID.randomUUID();
        UUID assignmentId = UUID.randomUUID();

        SubmitCodeRequest request = new SubmitCodeRequest();
        request.setProblemId(problemId);
        request.setLanguage("cpp");
        request.setCode("class Solution {}");
        request.setStartedAt(Instant.now());

        Problem classProblem = Problem.builder()
                .id(problemId)
                .type(ProblemType.CLASS)
                .build();

        AssignmentProblem assignmentProblem = AssignmentProblem.builder()
                .assignmentId(assignmentId)
                .problemId(problemId)
                .build();

        Assignment assignment = Assignment.builder()
                .id(assignmentId)
                .maxSubmission(3)
                .status(AssignmentStatus.PENDING)
                .build();

        RunCodeResponse runCodeResponse = RunCodeResponse.builder()
                .status(JudgeStatus.ACCEPTED)
                .runtime(8L)
                .passedTestcases(1)
                .totalTestcases(1)
                .testcases(List.<TestcaseResult>of())
                .build();

        Submission savedSubmission = Submission.builder()
                .id(UUID.randomUUID())
                .submittedAt(Instant.now())
                .score("100.0")
                .build();

        when(problemRepository.findByIdAndDeletedAtIsNull(problemId)).thenReturn(Optional.of(classProblem));
        when(assignmentProblemRepository.findByProblemId(problemId)).thenReturn(assignmentProblem);
        when(assignmentRepository.findByIdAndDeletedAtIsNull(assignmentId)).thenReturn(Optional.of(assignment));
        when(submissionRepository.countByUserIdAndAssignmentId(userId, assignmentId)).thenReturn(1L);
        when(executionService.runByTestcase(any())).thenReturn(runCodeResponse);
        when(submissionRepository.save(any(Submission.class))).thenReturn(savedSubmission);

        submissionService.submit(userId, request);

        verify(submissionRepository).countByUserIdAndAssignmentId(userId, assignmentId);
        ArgumentCaptor<UpdateAssignmentRequest> updateCaptor = ArgumentCaptor.forClass(UpdateAssignmentRequest.class);
        verify(assignmentService).updateAssignment(org.mockito.Mockito.eq(assignmentId), updateCaptor.capture());
        assertEquals(AssignmentStatus.SUBMITTED, updateCaptor.getValue().getStatus());
        assertNull(updateCaptor.getValue().getTitle());
    }
}
