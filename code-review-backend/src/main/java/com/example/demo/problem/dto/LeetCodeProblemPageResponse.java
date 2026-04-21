package com.example.demo.problem.dto;

import java.util.List;

import lombok.Data;

@Data
public class LeetCodeProblemPageResponse {

    private int total;
    private int page;
    private int limit;
    private List<LeetCodeProblemResponse> data;
}
