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
public class RecommendationResponse {

    private String studentId;

    private String currentExerciseId;

    private String anchorConcept;

    private String assignedPath;

    private String focusConceptId;

    private Integer criticalErrors;

    private Framework framework;

    private GraphSummary graphSummary;

    private ReferenceBlock reasoning;

    private ReferenceBlock roadmapSummary;

    private List<RoadmapStep> roadmap;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class Framework {
        private String riskLevel;
        private String readinessLevel;
        private String explanation;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class GraphSummary {
        private Double currentConceptWeight;
        private Double bestPathWeight;
        private Double bestRelatedExerciseWeight;
        private Double latestReviewImprovementSignal;
        private Double latestReviewSeverityChange;
        private Double latestSubmissionImprovementRatio;
        private Double latestSubmissionRegressionRatio;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class ReferenceBlock {
        private String content;
        private List<ReferenceItem> refs;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class ReferenceItem {
        private String refId;
        private String content;
        private String refCategory;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class RoadmapStep {
        private Integer step;
        private Exercise exercise;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class Exercise {
        private String exerciseId;
        private String title;
        private String description;
        private String content;
        private String difficulty;
        private List<String> tags;
        private List<String> conceptIds;
        private String directive;
    }
}
