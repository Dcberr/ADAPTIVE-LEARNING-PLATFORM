package com.example.demo.problem.dto;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.example.demo.problem.entity.ProblemType;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ProblemResponse {

    private UUID id;

    private String externalId;

    private String title;

    private String description;

    private String difficulty;

    private String problemConstraint;

    private ProblemType type;

    private Map<String, String> functionSkeletons;

    private List<TestcaseResponse> testcases;

    private List<String> similarQuestionIds;

    private List<String> tags;
}
