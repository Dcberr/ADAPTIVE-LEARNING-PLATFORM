package com.example.demo.problem.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.problem.dto.CreateTestcaseRequest;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.service.TestcaseService;

@RestController
@RequestMapping("/testcases")
@RequiredArgsConstructor
public class TestcaseController {

    private final TestcaseService testcaseService;

    @PostMapping
    public ApiResponse<TestcaseResponse> createTestcase(
            @RequestBody CreateTestcaseRequest request
    ) {

        return ApiResponse.success(
                testcaseService.createTestcase(request)
        );
    }

    @GetMapping("/problem/{problemId}")
    public ApiResponse<List<TestcaseResponse>> getTestcases(
            @PathVariable UUID problemId
    ) {

        return ApiResponse.success(
                testcaseService.getTestcasesByProblem(problemId)
        );
    }
}