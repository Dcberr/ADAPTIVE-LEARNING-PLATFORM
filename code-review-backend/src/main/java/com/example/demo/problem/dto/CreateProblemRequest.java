package com.example.demo.problem.dto;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CreateProblemRequest {

    private String description;
    private UUID assignmentId;

    private List<TestcaseRequest> testcases;

    @Data
    public static class TestcaseRequest {
        private String input;
        private String expectedOutput;
        private boolean isSample;
        private String explanation;
    }
}