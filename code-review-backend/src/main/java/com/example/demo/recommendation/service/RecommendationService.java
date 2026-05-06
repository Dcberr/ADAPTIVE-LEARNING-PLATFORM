package com.example.demo.recommendation.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.recommendation.dto.RecommendationHistoryResponse;
import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;

public interface RecommendationService {

    RecommendationResponse getRecommendation(RecommendationRequest request, UUID requesterId);

    List<RecommendationHistoryResponse> getRecommendationHistory(UUID studentId, UUID requesterId);

    List<RecommendationHistoryResponse> getRecommendationHistoryByProblem(UUID studentId, UUID problemId, UUID requesterId);
}
