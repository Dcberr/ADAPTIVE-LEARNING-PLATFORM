package com.example.demo.recommendation.service;

import java.util.UUID;

import com.example.demo.recommendation.dto.RecommendationRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;

public interface RecommendationService {

    RecommendationResponse getRecommendation(RecommendationRequest request, UUID requesterId);
}
