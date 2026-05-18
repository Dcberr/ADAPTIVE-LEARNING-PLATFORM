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
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.recommendation.entity.RecommendationHistory;
import com.example.demo.recommendation.repository.RecommendationHistoryRepository;
import com.example.demo.review.entity.CodeReview;
import com.example.demo.review.repository.CodeReviewRepository;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.entity.SubmissionStatus;
import com.example.demo.submission.repository.SubmissionRepository;

import java.util.Comparator;
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
    private final ProblemRepository problemRepository;
    private final CodeReviewRepository codeReviewRepository;
    private final RecommendationHistoryRepository recommendationHistoryRepository;

    @Override
    @Transactional
    public SubmissionResponse submit(
            UUID userId,
            SubmitCodeRequest request
    ) {
        Problem problem = problemRepository.findByIdAndDeletedAtIsNull(request.getProblemId())
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        Assignment assignment = resolveAssignmentForSubmission(userId, problem, request.getProblemId());

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

        if (assignment != null) {
            assignmentService.updateAssignment(assignment.getId(), UpdateAssignmentRequest.builder()
                    .status(AssignmentStatus.SUBMITTED)
                    .build());
        }

        return SubmissionResponse.builder()
                .submissionId(submission.getId())
                .userId(submission.getUserId())
                .status(SubmissionStatus.SUBMITTED)
                .startedAt(request.getStartedAt())
                .submittedAt(submission.getSubmittedAt())
                .score(submission.getScore())
                .build();
    }

    private Assignment resolveAssignmentForSubmission(UUID userId, Problem problem, UUID problemId) {
        if (problem.getType() == ProblemType.LIBRARY) {
            return null;
        }

        AssignmentProblem assignmentProblem = assignmentProblemRepository.findByProblemId(problemId);
        if (assignmentProblem == null) {
            throw new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND);
        }

        Assignment assignment = assignmentRepository.findByIdAndDeletedAtIsNull(assignmentProblem.getAssignmentId())
                .orElseThrow(() -> new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND));

        int maxSubmission = assignment.getMaxSubmission();
        if (maxSubmission > 0) {
            throwIfSubmissionLimitExceeded(userId, assignment);
        }

        return assignment;
    }

    private void throwIfSubmissionLimitExceeded(UUID userId, Assignment assignment) {
        long submissionsUsed = submissionRepository.countByUserIdAndAssignmentId(userId, assignment.getId());
        if (submissionsUsed >= assignment.getMaxSubmission()) {
            throw new AppException(ErrorCode.SUBMISSION_LIMIT_EXCEEDED);
        }
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

        Instant submittedAt = submission.getSubmittedAt();
        Instant nextSubmissionAt = findNextSubmissionAt(submission);
        List<CodeReview> reviews = codeReviewRepository.findBySubmissionId(submissionId).stream()
                .filter(review -> isOnOrAfter(review.getCreatedAt(), submittedAt))
                .filter(review -> isBeforeNextSubmission(review.getCreatedAt(), nextSubmissionAt))
                .sorted(Comparator.comparing(
                        CodeReview::getCreatedAt,
                        Comparator.nullsLast(Comparator.naturalOrder())
                ).thenComparing(
                        CodeReview::getId,
                        Comparator.nullsLast(Comparator.naturalOrder())
                ))
                .toList();

        boolean isReviewed = !reviews.isEmpty();
        boolean isRecommend = isRecommendationGeneratedForSubmission(submission, reviews, submittedAt, nextSubmissionAt);

        return SubmissionDetailResponse.builder()
                .code(submission.getCode())
                .language(submission.getLanguage())
                .isReviewed(isReviewed)
                .isRecommend(isRecommend)
                .testcaseResults(submission.getTestcaseResults())
                .build();
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

        private boolean isRecommendationGeneratedForSubmission(Submission submission, List<CodeReview> reviews,
                                                               Instant submittedAt, Instant nextSubmissionAt) {
            if (reviews.isEmpty()) {
                return false;
            }

            List<RecommendationHistory> recommendationHistories = recommendationHistoryRepository
                    .findByStudentIdAndProblemIdOrderByCreatedAtDesc(submission.getUserId(), submission.getProblemId());

            return recommendationHistories.stream()
                    .map(RecommendationHistory::getCreatedAt)
                    .filter(recommendationAt -> isOnOrAfter(recommendationAt, submittedAt))
                    .filter(recommendationAt -> isBeforeNextSubmission(recommendationAt, nextSubmissionAt))
                    .anyMatch(recommendationAt -> reviews.stream()
                            .map(CodeReview::getCreatedAt)
                            .anyMatch(reviewAt -> isOnOrAfter(recommendationAt, reviewAt)));
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

        @Override
        public List<SubmissionOverviewResponse> getProblemSubmissions(UUID problemId) {

            return submissionRepository.getSubmissionOverviewByProblem(problemId);      
        }

        @Override
        public List<Submission> getAllSubmissionsByProblemIdAndUserId(UUID userId, UUID problemId) {
            return submissionRepository.getAllSubmissionsByProblemIdAndUserId(userId, problemId);
        }
}
