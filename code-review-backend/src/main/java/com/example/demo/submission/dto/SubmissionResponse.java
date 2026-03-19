package com.example.demo.submission.dto;

import lombok.Builder;
import lombok.Data;

import java.util.UUID;

@Data
@Builder
public class SubmissionResponse {

    private UUID id;

    private String status;

    private Long runtime;

    private Integer passedTestcases;

    private Integer totalTestcases;
}