package com.example.demo.recommendation.dto;

import java.util.List;

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
public class RecommendationAgentRequest {

    private String studentId;

    private Exercise exercise;

    @Builder.Default
    private List<String> focusConceptIds = List.of();

    @Builder.Default
    private List<String> attemptedExerciseIds = List.of();

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class Exercise {
        private String exerciseId;
        private String slug;
        private String title;
        private String description;
        private String content;
        private String difficulty;
        @Builder.Default
        private List<String> conceptSlugs = List.of();
    }
}
