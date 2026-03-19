package com.example.demo.submission.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.service.SubmissionService;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/submissions")
@RequiredArgsConstructor
public class SubmissionController {

    private final SubmissionService submissionService;

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

    @GetMapping("/me")
    public ApiResponse<List<SubmissionOverviewResponse>> overview(
            Authentication auth
    ) {

        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                submissionService.getUserSubmissionOverview(userId)
        );
    }

    @GetMapping("/{submissionId}")
    public ApiResponse<SubmissionDetailResponse> detail(
            @PathVariable UUID submissionId
    ) {

        return ApiResponse.success(
                submissionService.getSubmissionDetail(submissionId)
        );
    }

    @GetMapping("/problem/{problemId}")
        public ApiResponse<List<SubmissionOverviewResponse>> getProblemSubmissions(
                @PathVariable UUID problemId
        ) {

        return ApiResponse.success(
                submissionService.getProblemSubmissions(problemId)
        );
    }
}