package com.example.demo.problem.dto;

import java.util.Map;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ProblemResponse {

    private UUID id;

    // private String title;

    private String description;

    private String problemConstraint;

    /**
     * Function skeleton for each language
     * Contains only the function to implement, without main() or boilerplate
     */
    private Map<String, String> functionSkeletons;

}