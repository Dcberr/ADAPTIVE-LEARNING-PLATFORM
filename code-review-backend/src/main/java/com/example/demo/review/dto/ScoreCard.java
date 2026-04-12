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
public class ScoreCard {
    @JsonProperty("problem_solving_creativity")
    private ScoreCardItem problem_solving_creativity;
    @JsonProperty("logic_traceability")
    private ScoreCardItem logic_traceability;
    @JsonProperty("generalization_score")
    private ScoreCardItem generalization_score;
    @JsonProperty("construct_appropriateness")
    private ScoreCardItem construct_appropriateness;
    @JsonProperty("self_correction_path")
    private ScoreCardItem self_correction_path;
    @JsonProperty("variable_understanding")
    private ScoreCardItem variable_understanding;
    @JsonProperty("control_flow_understanding")
    private ScoreCardItem control_flow_understanding;
    @JsonProperty("input_output_awareness")
    private ScoreCardItem input_output_awareness;
    @JsonProperty("edge_case_awareness")
    private ScoreCardItem edge_case_awareness;
    @JsonProperty("debugging_readiness")
    private ScoreCardItem debugging_readiness;

}
