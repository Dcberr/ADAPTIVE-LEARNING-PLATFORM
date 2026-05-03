package com.example.demo.submission.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.assignment.service.AssignmentService;
import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.entity.SubmissionStatus;
import com.example.demo.submission.repository.SubmissionRepository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubmissionServiceImpl implements SubmissionService {

    private final SubmissionRepository submissionRepository;
    private final ExecutionService executionService;
    private final AssignmentService assignmentService;
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final AssignmentRepository assignmentRepository;

    @Override
    @Transactional
    public SubmissionResponse submit(
            UUID userId,
            SubmitCodeRequest request
    ) {
        AssignmentProblem assignmentProblem = assignmentProblemRepository.findByProblemId(request.getProblemId());

        if (assignmentProblem == null) {
            throw new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND);
        }

        Assignment assignment = assignmentRepository.findByIdAndDeletedAtIsNull(assignmentProblem.getAssignmentId())
                .orElseThrow(() -> new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND));

        int maxSubmission = assignment.getMaxSubmission();
        if (maxSubmission > 0) {
            long submissionsUsed = submissionRepository.countByUserIdAndAssignmentId(userId, assignment.getId());
            if (submissionsUsed >= maxSubmission) {
                throw new AppException(ErrorCode.SUBMISSION_LIMIT_EXCEEDED);
            }
        }

        RunTestcaseRequest judgeRequest = new RunTestcaseRequest();

        judgeRequest.setProblemId(request.getProblemId());
        judgeRequest.setLanguage(request.getLanguage());
        judgeRequest.setCode(request.getCode());

        RunCodeResponse result =
                executionService.runByTestcase(judgeRequest);

        Submission submission = submissionRepository.save(
                Submission.builder()
                        .userId(userId)
                        .problemId(request.getProblemId())
                        .language(request.getLanguage())
                        .code(request.getCode())
                        .status(SubmissionStatus.SUBMITTED)
                        .runtime(result.getRuntime())
                        .passedTestcases(result.getPassedTestcases())
                        .totalTestcases(result.getTotalTestcases())
                        .score(String.valueOf((double) result.getPassedTestcases() / result.getTotalTestcases() * 100))
                        .startedAt(request.getStartedAt())
                        .submittedAt(Instant.now())
                        .testcaseResults(result.getTestcases())
                        
                        .build()
        );

        assignmentService.updateAssignment(assignment.getId(),UpdateAssignmentRequest.builder()
                .status(AssignmentStatus.SUBMITTED)
                .build());

        return SubmissionResponse.builder()
                .submissionId(submission.getId())
                .status(SubmissionStatus.SUBMITTED)
                .startedAt(request.getStartedAt())
                .submittedAt(submission.getSubmittedAt())
                .score(submission.getScore())
                .build();
    }

    @Override
    public List<SubmissionResponse> getUserSubmissionsByAssignmentId(UUID userId, UUID assignmentId) {

        return submissionRepository.getUserSubmissionsByAssignmentId(userId, assignmentId);     
    }

    @Override
    public List<SubmissionOverviewResponse> getUserSubmissionOverview(UUID userId) {
        log.info(submissionRepository.getSubmissionOverview(userId).toString());
        SubmissionOverviewResponse response = submissionRepository.getSubmissionOverview(userId).get(0);
        return submissionRepository.getSubmissionOverview(userId);
    }

    @Override
    public List<SubmissionResponse> getAllSubmissionsByAssignmentId(UUID assignmentId) {
        return submissionRepository.getAllSubmissionsByAssignmentId(assignmentId);
    }
    
    @Override
    public SubmissionDetailResponse getSubmissionDetail(UUID submissionId) {

        Submission submission = submissionRepository.findById(submissionId)
                .orElseThrow(() -> new RuntimeException("Submission not found"));

        return SubmissionDetailResponse.builder()
                .code(submission.getCode())
                .language(submission.getLanguage())
                .testcaseResults(submission.getTestcaseResults())
                .build();
        }

        @Override
        public List<SubmissionOverviewResponse> getProblemSubmissions(UUID problemId) {

            return submissionRepository.getSubmissionOverviewByProblem(problemId);      
        }

        @Override
        public List<Submission> getAllSubmissionsByProblemIdAndUserId(UUID userId, UUID problemId) {
            return submissionRepository.getAllSubmissionsByProblemIdAndUserId(userId, problemId);
        }
}
