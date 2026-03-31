package com.example.demo.submission.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.service.SubmissionService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.List;
import java.util.UUID;

@Tag(name = "Submission", description = "APIs for code submission and results")
@RestController
@RequestMapping("/submissions")
@RequiredArgsConstructor
public class SubmissionController {

    private final SubmissionService submissionService;

    @Operation(summary = "Submit code for a problem")
    @PostMapping
    public ApiResponse<SubmissionResponse> submit(
            Authentication auth,
            @RequestBody SubmitCodeRequest request
    ) {
        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                submissionService.submit(userId, request)
        );
    }

    @Operation(summary = "Get current user's submissions overview")
    @GetMapping("/me")
    public ApiResponse<List<SubmissionOverviewResponse>> overview(
            Authentication auth
    ) {
        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                submissionService.getUserSubmissionOverview(userId)
        );
    }

    @Operation(summary = "Get submission detail")
    @GetMapping("/{submissionId}")
    public ApiResponse<SubmissionDetailResponse> detail(
            @Parameter(description = "Submission ID")
            @PathVariable UUID submissionId
    ) {
        return ApiResponse.success(
                submissionService.getSubmissionDetail(submissionId)
        );
    }

    @Operation(summary = "Get submissions of a problem")
    @GetMapping("/problem/{problemId}")
    public ApiResponse<List<SubmissionOverviewResponse>> getProblemSubmissions(
            @Parameter(description = "Problem ID")
            @PathVariable UUID problemId
    ) {
        return ApiResponse.success(
                submissionService.getProblemSubmissions(problemId)
        );
    }
}