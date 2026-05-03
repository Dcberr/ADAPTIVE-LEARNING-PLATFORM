package com.example.demo.problem.dto;

import java.util.List;
import java.util.Map;

import lombok.Data;

@Data
public class UpdateLibraryProblemRequest {

    private String title;

    private String description;

    private String difficulty;

    private String constraints;

    private Map<String, String> starterCodes;

    private List<TestcaseDto> testcases;

    private List<String> tags;
}
