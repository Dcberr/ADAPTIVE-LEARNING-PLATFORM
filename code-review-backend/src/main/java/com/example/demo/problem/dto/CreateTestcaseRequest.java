package com.example.demo.problem.dto;

import java.util.UUID;

import lombok.Data;

@Data
public class CreateTestcaseRequest {

    private UUID problemId;

    private String input;

    private String expectedOutput;

    private boolean isSample;

}