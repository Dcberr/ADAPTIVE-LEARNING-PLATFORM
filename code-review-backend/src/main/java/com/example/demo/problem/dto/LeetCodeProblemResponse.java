package com.example.demo.problem.dto;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class LeetCodeProblemResponse {

    private String title;
    private String difficulty;
    private String content;
    private List<String> constraints;
    private Map<String, LeetCodeProblemExampleResponse> examples;

    @JsonProperty("code_snippet")
    private String codeSnippet;
}
