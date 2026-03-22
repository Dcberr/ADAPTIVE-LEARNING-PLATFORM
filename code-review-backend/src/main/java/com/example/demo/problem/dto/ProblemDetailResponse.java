package com.example.demo.problem.dto;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ProblemDetailResponse {

    private UUID id;

    private String title;

    private String description;

    private String difficulty;

    private String source;

    private List<TestcaseResponse> sampleTestcases;

}