package com.example.demo.review.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewItem {
    private LineContext line;
    private ColumnContext column;
    @JsonProperty("code_snippet")
    private String code_snippet;
    private ReviewItemType type;
    private String issue;
    @JsonProperty("fix_suggestion")
    private String fix_suggestion;
    @JsonProperty("review_link")
    private ReviewLink review_link;

    private enum ReviewItemType {
        Error,
        Warning,
    }
}
