package com.example.demo.review.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewLink {
    @JsonProperty("current_issue")
    private String current_issue;
    @JsonProperty("current_code_snippet")
    private String current_code_snippet;
    @JsonProperty("previous_submission_indexes")
    private List<Integer> previous_submission_indexes;
    @JsonProperty("previous_code_snippet")
    private String previous_code_snippet;
    @JsonProperty("what_improved")
    private String what_improved;
    @JsonProperty("what_still_needs_work")
    private String what_still_needs_work;
    @JsonProperty("relation_summary")
    private String relation_summary;
}
