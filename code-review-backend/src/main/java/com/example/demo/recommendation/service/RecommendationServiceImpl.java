package com.example.demo.recommendation.service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemTag;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.ProblemTagRepository;
import com.example.demo.recommendation.client.RecommendationAgentClient;
import com.example.demo.recommendation.dto.RecommendationAgentRequest;
import com.example.demo.recommendation.dto.RecommendationHistoryResponse;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;
import com.example.demo.recommendation.entity.RecommendationHistory;
import com.example.demo.recommendation.repository.RecommendationHistoryRepository;
import com.example.demo.review.dto.ReviewResponse;
import com.example.demo.review.entity.CodeReview;
import com.example.demo.review.repository.CodeReviewRepository;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.repository.SubmissionRepository;
import com.example.demo.user.entity.Role;
import com.example.demo.user.entity.User;
import com.example.demo.user.repository.UserRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Instant;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class RecommendationServiceImpl implements RecommendationService {

    private final RecommendationAgentClient recommendationAgentClient;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final ProblemTagRepository problemTagRepository;
    private final SubmissionRepository submissionRepository;
    private final CodeReviewRepository codeReviewRepository;
    private final RecommendationHistoryRepository recommendationHistoryRepository;
    private final ObjectMapper objectMapper;

    @Override
    @Transactional
    public RecommendationResponse getRecommendation(RecommendationRequest request, UUID requesterId) {
        if (request.getStudentId() == null || request.getCurrentExerciseId() == null) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        User requester = getUserOrThrow(requesterId);
        User student = getUserOrThrow(request.getStudentId());
        Problem problem = getProblemOrThrow(request.getCurrentExerciseId());
        validateAccess(requester, student.getId());

        RecommendationResponse response = recommendationAgentClient.getRecommendation(
                buildAgentRequest(request, problem)
        );
        RecommendationResponse remappedResponse = remapRecommendationExerciseIds(response);
        saveRecommendationHistory(student.getId(), problem.getId(), requesterId, remappedResponse);
        return remappedResponse;
    }

    @Override
    @Transactional(readOnly = true)
    public List<RecommendationHistoryResponse> getRecommendationHistory(UUID studentId, UUID requesterId) {
        User requester = getUserOrThrow(requesterId);
        User student = getUserOrThrow(studentId);
        validateAccess(requester, student.getId());

        return recommendationHistoryRepository.findByStudentIdOrderByCreatedAtDesc(studentId).stream()
                .map(this::toHistoryResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<RecommendationHistoryResponse> getRecommendationHistoryByProblem(UUID studentId, UUID problemId, UUID requesterId) {
        User requester = getUserOrThrow(requesterId);
        User student = getUserOrThrow(studentId);
        getProblemOrThrow(problemId);
        validateAccess(requester, student.getId());

        return recommendationHistoryRepository.findByStudentIdAndProblemIdOrderByCreatedAtDesc(studentId, problemId)
                .stream()
                .map(this::toHistoryResponse)
                .toList();
    }

    private RecommendationAgentRequest buildAgentRequest(
            RecommendationRequest request,
            Problem problem
    ) {
        String exerciseId = request.getCurrentExerciseId().toString();
        String title = safe(problem.getTitle());
        String description = safe(problem.getDescription());
        String content = !safe(problem.getProblemConstraint()).isBlank()
                ? safe(problem.getProblemConstraint())
                : description;
        Optional<Submission> latestSubmission = resolveLatestSubmittedSubmission(
                request.getStudentId(),
                problem.getId()
        );

        return RecommendationAgentRequest.builder()
                .studentId(request.getStudentId().toString())
                .exercise(RecommendationAgentRequest.Exercise.builder()
                        .exerciseId(exerciseId)
                        .slug(!safe(problem.getExternalId()).isBlank() ? safe(problem.getExternalId()) : exerciseId)
                        .title(!title.isBlank() ? title : exerciseId)
                        .description(description)
                        .content(content)
                        .difficulty(safe(problem.getDifficulty()))
                        .conceptSlugs(problemTagRepository.findByProblemId(problem.getId()).stream()
                                .map(ProblemTag::getTag)
                                .filter(tag -> tag != null && !tag.isBlank())
                                .toList())
                        .build())
                .review(latestSubmission
                        .flatMap(submission -> resolveLatestReview(submission.getId()))
                        .orElse(null))
                .submission(latestSubmission
                        .map(this::toRecommendationSubmission)
                        .orElse(null))
                .focusConceptIds(resolveFocusConceptIds(problem))
                .attemptedExerciseIds(resolveAttemptedExerciseIds(request.getStudentId()))
                .build();
    }

    private Optional<Submission> resolveLatestSubmittedSubmission(UUID studentId, UUID problemId) {
        return submissionRepository.getAllSubmissionsByProblemIdAndUserId(studentId, problemId).stream()
                .filter(submission -> submission.getSubmittedAt() != null)
                .max(Comparator.comparing(Submission::getSubmittedAt)
                        .thenComparing(Submission::getId));
    }

    private Optional<RecommendationAgentRequest.Review> resolveLatestReview(UUID submissionId) {
        return codeReviewRepository.findBySubmissionId(submissionId).stream()
                .max(Comparator.comparing(
                                CodeReview::getCreatedAt,
                                Comparator.nullsLast(Comparator.naturalOrder())
                        )
                        .thenComparing(
                                CodeReview::getId,
                                Comparator.nullsLast(Comparator.naturalOrder())
                        ))
                .map(this::toRecommendationReview);
    }

    private RecommendationAgentRequest.Review toRecommendationReview(CodeReview review) {
        ReviewResponse storedReview = deserializeStoredReview(review);

        return RecommendationAgentRequest.Review.builder()
                .reviewId(review.getId() != null ? review.getId().toString() : safe(storedReview.getReview_id()))
                .summary(!safe(review.getSummary()).isBlank() ? safe(review.getSummary()) : safe(storedReview.getSummary()))
                .detail(!safe(review.getDetail()).isBlank() ? safe(review.getDetail()) : safe(storedReview.getDetail()))
                .reviewItems(storedReview.getReview_items() != null ? storedReview.getReview_items() : List.of())
                .build();
    }

    private RecommendationAgentRequest.Submission toRecommendationSubmission(Submission submission) {
        return RecommendationAgentRequest.Submission.builder()
                .submissionId(submission.getId() != null ? submission.getId().toString() : "")
                .code(safe(submission.getCode()))
                .testcases(submission.getTestcaseResults() == null
                        ? List.of()
                        : submission.getTestcaseResults().stream()
                                .map(testcase -> RecommendationAgentRequest.SubmissionTestCase.builder()
                                        .input(safe(testcase.getInput()))
                                        .expect(safe(testcase.getExpectedOutput()))
                                        .output(safe(testcase.getOutput()))
                                        .build())
                                .toList())
                .createdAt(submission.getSubmittedAt() != null ? submission.getSubmittedAt().toString() : "")
                .build();
    }

    private ReviewResponse deserializeStoredReview(CodeReview review) {
        try {
            return review.getReviewItemsJson() == null || review.getReviewItemsJson().isBlank()
                    ? ReviewResponse.builder().build()
                    : objectMapper.readValue(review.getReviewItemsJson(), ReviewResponse.class);
        } catch (JsonProcessingException ex) {
            log.warn("Failed to deserialize stored review for recommendation, reviewId={}", review.getId(), ex);
            return ReviewResponse.builder().build();
        }
    }

    private java.util.List<String> resolveFocusConceptIds(Problem problem) {
        return problemTagRepository.findByProblemId(problem.getId()).stream()
                .map(ProblemTag::getTag)
                .filter(tag -> tag != null && !tag.isBlank())
                .findFirst()
                .map(java.util.List::of)
                .orElseGet(java.util.List::of);
    }

    private java.util.List<String> resolveAttemptedExerciseIds(UUID studentId) {
        return submissionRepository.findDistinctProblemIdsByUserId(studentId).stream()
                .map(UUID::toString)
                .toList();
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }

    private User getUserOrThrow(UUID userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
    }

    private Problem getProblemOrThrow(UUID problemId) {
        return problemRepository.findByIdAndDeletedAtIsNull(problemId)
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));
    }

    private void validateAccess(User requester, UUID studentId) {
        boolean canAccess = requester.getId().equals(studentId)
                || requester.getRole() == Role.INSTRUCTOR
                || requester.getRole() == Role.ADMIN;

        if (!canAccess) {
            throw new AppException(ErrorCode.FORBIDDEN);
        }
    }

    private void saveRecommendationHistory(UUID studentId, UUID problemId, UUID requesterId,
                                           RecommendationResponse recommendationResponse) {
        try {
            recommendationHistoryRepository.save(RecommendationHistory.builder()
                    .studentId(studentId)
                    .problemId(problemId)
                    .requestedBy(requesterId)
                    .summary(recommendationResponse != null ? recommendationResponse.getSummary() : null)
                    .recommendationJson(objectMapper.writeValueAsString(recommendationResponse))
                    .createdAt(Instant.now())
                    .build());
        } catch (JsonProcessingException ex) {
            log.error("Failed to serialize recommendation history for studentId={} problemId={}", studentId, problemId,
                    ex);
            throw new AppException(ErrorCode.INTERNAL_ERROR);
        }
    }

    private RecommendationHistoryResponse toHistoryResponse(RecommendationHistory history) {
        try {
            return RecommendationHistoryResponse.builder()
                    .recommendationId(history.getId())
                    .studentId(history.getStudentId())
                    .problemId(history.getProblemId())
                    .requestedBy(history.getRequestedBy())
                    .createdAt(history.getCreatedAt())
                    .recommendation(objectMapper.readValue(history.getRecommendationJson(), RecommendationResponse.class))
                    .build();
        } catch (JsonProcessingException ex) {
            log.error("Failed to deserialize recommendation history id={}", history.getId(), ex);
            throw new AppException(ErrorCode.INTERNAL_ERROR);
        }
    }

    private RecommendationResponse remapRecommendationExerciseIds(RecommendationResponse response) {
        if (response == null || response.getRoadmap() == null || response.getRoadmap().isEmpty()) {
            return response;
        }

        LinkedHashSet<String> externalIds = response.getRoadmap().stream()
                .filter(step -> step.getExercises() != null)
                .flatMap(step -> step.getExercises().stream())
                .map(RecommendationResponse.RoadmapExercise::getExercise)
                .filter(exercise -> exercise != null && exercise.getSlug() != null && !exercise.getSlug().isBlank())
                .map(RecommendationResponse.Exercise::getSlug)
                .collect(Collectors.toCollection(LinkedHashSet::new));

        if (externalIds.isEmpty()) {
            return response;
        }

        Map<String, Problem> problemsByExternalId = problemRepository
                .findAllBySourceAndExternalIdIn("LEETCODE", externalIds)
                .stream()
                .collect(Collectors.toMap(Problem::getExternalId, Function.identity(), (left, right) -> left));

        ArrayList<String> unmappedExternalIds = new ArrayList<>();
        for (String externalId : externalIds) {
            if (!problemsByExternalId.containsKey(externalId)) {
                unmappedExternalIds.add(externalId);
            }
        }
        if (!unmappedExternalIds.isEmpty()) {
            log.warn("Recommendation returned exercises not found in local problems table for externalIds={}",
                    unmappedExternalIds);
        }

        for (RecommendationResponse.RoadmapStep step : response.getRoadmap()) {
            if (step.getExercises() == null) {
                continue;
            }
            for (RecommendationResponse.RoadmapExercise roadmapExercise : step.getExercises()) {
                RecommendationResponse.Exercise exercise = roadmapExercise.getExercise();
                if (exercise == null) {
                    continue;
                }
                String externalId = safe(exercise.getSlug());
                Problem mappedProblem = problemsByExternalId.get(externalId);
                if (mappedProblem != null) {
                    exercise.setExerciseId(mappedProblem.getId().toString());
                }
            }
        }

        return response;
    }
}
