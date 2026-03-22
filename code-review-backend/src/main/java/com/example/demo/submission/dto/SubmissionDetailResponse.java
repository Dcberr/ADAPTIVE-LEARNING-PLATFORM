package com.example.demo.submission.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.UUID;

import com.example.demo.problem.dto.TestcaseResponse;

@Data
@Builder
public class SubmissionDetailResponse {

    private UUID submissionId;

    private String problemTitle;

    private String problemDescription;

    private String score;

    private String difficulty;

    private String code;

    private String language;

    private String status;

    private List<TestcaseResponse> testcases;

}