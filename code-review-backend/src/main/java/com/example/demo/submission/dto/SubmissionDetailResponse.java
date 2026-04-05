package com.example.demo.submission.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import com.example.demo.execution.dto.TestcaseResult;
import com.example.demo.problem.dto.TestcaseResponse;

@Data
@Builder
public class SubmissionDetailResponse {

    private String code;

    private String language;

    @JdbcTypeCode(SqlTypes.JSON)
    private List<TestcaseResult> testcaseResults;

}