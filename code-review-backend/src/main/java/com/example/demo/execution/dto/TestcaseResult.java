package com.example.demo.execution.dto;

import com.example.demo.execution.model.JudgeStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class TestcaseResult {

    private int index;
    private String input;
    private String expectedOutput;
    private String output;
    private String error;
    private JudgeStatus status;
    private long runtime;
}
