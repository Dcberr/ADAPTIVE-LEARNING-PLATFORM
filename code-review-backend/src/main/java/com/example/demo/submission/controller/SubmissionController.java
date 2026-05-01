package com.example.demo.submission.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.entity.Submission;
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

    @Operation(summary = "Get my submissions by assignmennt")
    @GetMapping("/assignment/{assignmentId}/me")
    public ApiResponse<List<SubmissionResponse>> overview(
            Authentication auth,
            @PathVariable UUID assignmentId
    ) {
        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                submissionService.getUserSubmissionsByAssignmentId(userId, assignmentId)
        );
    }

    @Operation(summary = "Get current user's submissions by assignmennt")
    @GetMapping("/assignment/{assignmentId}/{userId}")
    public ApiResponse<List<SubmissionResponse>> overview(
            @PathVariable UUID userId,
            @PathVariable UUID assignmentId
    ) {
        return ApiResponse.success(
                submissionService.getUserSubmissionsByAssignmentId(userId, assignmentId)
        );
    }

    @Operation(summary = "Get all submissions by assignmennt")
    @GetMapping("/assignment/{assignmentId}")
    public ApiResponse<List<SubmissionResponse>> overview(
            @PathVariable UUID assignmentId
    ) {
        return ApiResponse.success(
                submissionService.getAllSubmissionsByAssignmentId(assignmentId)
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

    @Operation(summary = "Get user submission for a problem")
    @GetMapping("/problem/{problemId}/{userId}")
    public ApiResponse<List<Submission>> getUserSubmissionsByProblemIdAndUserId(
            @PathVariable UUID problemId,
            @PathVariable UUID userId
    ) {
        return ApiResponse.success(
                submissionService.getAllSubmissionsByProblemIdAndUserId(userId, problemId)
        );
    }
}