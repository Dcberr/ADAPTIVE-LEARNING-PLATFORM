package com.example.demo.recommendation.service;

import java.util.UUID;
import java.util.LinkedHashSet;
import java.util.ArrayList;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

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

        RecommendationResponse response = recommendationAgentClient.getRecommendation(
                buildAgentRequest(request, problem)
        );
        return remapRecommendationExerciseIds(response);
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
