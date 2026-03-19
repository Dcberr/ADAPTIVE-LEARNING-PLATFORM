package com.example.demo.review.dto;

import lombok.*;

import java.util.List;

import com.example.demo.execution.dto.TestcaseResult;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewResponse {

    private String summary;

    private String detail;

    private List<TestcaseResult> testcaseResults;

}