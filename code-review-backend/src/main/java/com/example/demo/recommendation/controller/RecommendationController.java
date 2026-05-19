package com.example.demo.recommendation.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.recommendation.dto.RecommendationHistoryResponse;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;
import com.example.demo.recommendation.service.RecommendationService;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@Tag(name = "Recommendation", description = "APIs for exercise recommendations and roadmap")
@RestController
@RequestMapping("/recommendations")
@RequiredArgsConstructor
public class RecommendationController {

    private final RecommendationService recommendationService;

    @Operation(summary = "Get recommended learning roadmap for a student on the current exercise")
    @PostMapping
    public ApiResponse<RecommendationResponse> getRecommendation(
            Authentication authentication,
            @RequestBody RecommendationRequest request
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendation(request, requesterId));
    }

    @Operation(summary = "Get my recommendation history")
    @Hidden
    @GetMapping("/history/me")
    public ApiResponse<List<RecommendationHistoryResponse>> getMyRecommendationHistory(
            Authentication authentication
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendationHistory(requesterId, requesterId));
    }

    @Operation(summary = "Get my recommendation history for a problem")
    @GetMapping("/history/problem/{problemId}/me")
    public ApiResponse<List<RecommendationHistoryResponse>> getMyRecommendationHistoryByProblem(
            Authentication authentication,
            @PathVariable UUID problemId
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendationHistoryByProblem(requesterId, problemId, requesterId));
    }

    @Operation(summary = "Get my recommendation history for a submission")
    @GetMapping("/history/submission/{submissionId}/me")
    public ApiResponse<List<RecommendationHistoryResponse>> getMyRecommendationHistoryBySubmission(
            Authentication authentication,
            @PathVariable UUID submissionId
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendationHistoryBySubmission(submissionId, requesterId));
    }

    @Operation(summary = "Get recommendation history of a student")
    @Hidden
    @GetMapping("/history/student/{studentId}")
    public ApiResponse<List<RecommendationHistoryResponse>> getRecommendationHistory(
            Authentication authentication,
            @PathVariable UUID studentId
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendationHistory(studentId, requesterId));
    }

    @Operation(summary = "Get recommendation history of a student for a problem")
    @GetMapping("/history/student/{studentId}/problem/{problemId}")
    public ApiResponse<List<RecommendationHistoryResponse>> getRecommendationHistoryByProblem(
            Authentication authentication,
            @PathVariable UUID studentId,
            @PathVariable UUID problemId
    ) {
        UUID requesterId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(recommendationService.getRecommendationHistoryByProblem(studentId, problemId, requesterId));
    }
}
