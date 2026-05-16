package com.example.demo.recommendation.dto;

import java.util.List;

import com.example.demo.review.dto.ReviewItem;
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

    private Review review;

    private Submission submission;

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

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class Review {
        private String reviewId;
        private String summary;
        private String detail;
        @Builder.Default
        private List<ReviewItem> reviewItems = List.of();
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class Submission {
        private String submissionId;
        private String code;
        @Builder.Default
        private List<SubmissionTestCase> testcases = List.of();
        private String createdAt;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class SubmissionTestCase {
        private String input;
        private String expect;
        private String output;
    }
}
