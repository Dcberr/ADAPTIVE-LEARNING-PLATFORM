package com.example.demo.problem.dto;

import java.util.UUID;

import lombok.Data;

@Data
public class CreateProblemRequest {

    private String title;

    private String description;

    private String difficulty;

    private UUID assignmentId;  

    private String source;

}