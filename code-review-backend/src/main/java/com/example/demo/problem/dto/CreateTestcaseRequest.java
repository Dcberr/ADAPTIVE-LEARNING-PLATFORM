package com.example.demo.problem.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CreateTestcaseRequest {

    private UUID problemId;

    private String input;

    private String expectedOutput;

    private boolean isHidden;

    private String explanation;

}