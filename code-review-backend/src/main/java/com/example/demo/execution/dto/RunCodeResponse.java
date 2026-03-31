package com.example.demo.execution.dto;

import java.util.List;

import com.example.demo.execution.model.JudgeStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class RunCodeResponse {

    private JudgeStatus status;
    private List<TestcaseResult> testcases;

    private int passedTestcases;
    private int totalTestcases;

}