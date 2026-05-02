package com.example.demo.problem.dto;

import java.util.List;
import java.util.Map;

import lombok.Data;

@Data
public class ProblemLibraryRequest {

    private String title;

    private String description;

    private String difficulty;

    private String constraints;

    private Map<String, String> starterCodes;

    private List<TestcaseDto> testcases;

    // private List<String> similarQuestionIds;

    private List<String> tags;

    // @Data
    // public static class TestcaseRequest {
    //     private String input;
    //     private String expectedOutput;
    //     private boolean isHidden;
    //     private String explanation;
    // }
}
