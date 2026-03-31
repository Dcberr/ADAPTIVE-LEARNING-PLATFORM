package com.example.demo.problem.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.problem.dto.CreateTestcaseRequest;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.service.TestcaseService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Testcase", description = "APIs for managing problem testcases")
@RestController
@RequestMapping("/testcases")
@RequiredArgsConstructor
public class TestcaseController {

    private final TestcaseService testcaseService;

    @Operation(summary = "Create a testcase for a problem")
    @PostMapping
    public ApiResponse<TestcaseResponse> createTestcase(
            @RequestBody CreateTestcaseRequest request
    ) {
        return ApiResponse.success(
                testcaseService.createTestcase(request)
        );
    }

    @Operation(summary = "Get testcases by problem ID")
    @GetMapping("/problem/{problemId}")
    public ApiResponse<List<TestcaseResponse>> getTestcases(
            @Parameter(description = "Problem ID")
            @PathVariable UUID problemId
    ) {
        return ApiResponse.success(
                testcaseService.getTestcasesByProblem(problemId)
        );
    }
}