package com.example.demo.problem.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ProblemResponse {

    private UUID id;

    private String title;

    private String description;

    private String difficulty;

    private String source;

}