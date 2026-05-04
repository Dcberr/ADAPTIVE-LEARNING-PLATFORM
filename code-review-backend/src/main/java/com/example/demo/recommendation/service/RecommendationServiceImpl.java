package com.example.demo.recommendation.service;

import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemTag;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.ProblemTagRepository;
import com.example.demo.recommendation.client.RecommendationAgentClient;
import com.example.demo.recommendation.dto.RecommendationAgentRequest;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;
import com.example.demo.submission.repository.SubmissionRepository;
import com.example.demo.user.entity.Role;
import com.example.demo.user.entity.User;
import com.example.demo.user.repository.UserRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class RecommendationServiceImpl implements RecommendationService {

    private final RecommendationAgentClient recommendationAgentClient;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final ProblemTagRepository problemTagRepository;
    private final SubmissionRepository submissionRepository;

    @Override
    public RecommendationResponse getRecommendation(RecommendationRequest request, UUID requesterId) {
        User requester = userRepository.findById(requesterId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        if (request.getStudentId() == null || request.getCurrentExerciseId() == null) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        userRepository.findById(request.getStudentId())
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        Problem problem = problemRepository.findById(request.getCurrentExerciseId())
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        boolean canAccess = requesterId.equals(request.getStudentId())
                || requester.getRole() == Role.INSTRUCTOR
                || requester.getRole() == Role.ADMIN;

        if (!canAccess) {
            throw new AppException(ErrorCode.FORBIDDEN);
        }

        return recommendationAgentClient.getRecommendation(buildAgentRequest(request, problem));
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
                .focusConceptIds(resolveFocusConceptIds(problem))
                .attemptedExerciseIds(resolveAttemptedExerciseIds(request.getStudentId()))
                .build();
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
}
