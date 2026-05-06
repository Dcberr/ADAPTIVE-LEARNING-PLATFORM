package com.example.demo.recommendation.dto;

import java.time.Instant;
import java.util.UUID;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class RecommendationHistoryResponse {

    private UUID recommendationId;

    private UUID studentId;

    private UUID problemId;

    private UUID requestedBy;

    private Instant createdAt;

    private RecommendationResponse recommendation;
}
