package com.example.demo.execution.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ExecutionResult {

    private String stdout;

    private String stderr;

    private int exitCode;

    private Long runtime;

}