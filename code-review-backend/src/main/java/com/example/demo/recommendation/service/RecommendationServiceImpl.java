package com.example.demo.recommendation.service;

import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.recommendation.client.RecommendationAgentClient;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;
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

    @Override
    public RecommendationResponse getRecommendation(RecommendationRequest request, UUID requesterId) {
        User requester = userRepository.findById(requesterId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        if (request.getStudentId() == null || request.getCurrentExerciseId() == null) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        userRepository.findById(request.getStudentId())
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

        problemRepository.findById(request.getCurrentExerciseId())
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        boolean canAccess = requesterId.equals(request.getStudentId())
                || requester.getRole() == Role.INSTRUCTOR
                || requester.getRole() == Role.ADMIN;

        if (!canAccess) {
            throw new AppException(ErrorCode.FORBIDDEN);
        }

        return recommendationAgentClient.getRecommendation(request);
    }
}
