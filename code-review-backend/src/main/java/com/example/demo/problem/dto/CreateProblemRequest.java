package com.example.demo.problem.dto;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CreateProblemRequest {

    private String description;
    private String title;             
    private String difficulty; 
    private UUID assignmentId;
    private String problemConstraint;
    private Map<String, String> starterCodes;
    // private String leetCodeCodeSnippet;
    // private String leetCodeLanguage;

    private List<TestcaseDto> testcases;

    // private List<String> similarQuestionIds;

    // @Data
    // public static class TestcaseRequest {
    //     private String input;
    //     private String expectedOutput;
    //     private boolean isHidden;
    //     private String explanation;
    // }
}
