package com.example.demo.recommendation.controller;

import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;
import com.example.demo.recommendation.service.RecommendationService;

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
}
