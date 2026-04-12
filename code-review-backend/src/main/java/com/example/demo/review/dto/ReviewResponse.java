package com.example.demo.review.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.util.List;

import com.example.demo.execution.dto.TestcaseResult;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewResponse {

    @JsonProperty("review_id")
    private String review_id;

    private String summary;

    private String detail;

    @JsonProperty("review_items")
    private List<ReviewItem> review_items;

    // private List<TestcaseResult> testcaseResults;
    @JsonProperty("scorecard")
    private ScoreCard scoreCard;

}