package com.example.demo.review.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.review.dto.ReviewResponse;
import com.example.demo.review.service.ReviewService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.List;
import java.util.UUID;

@Tag(name = "Review", description = "APIs for code review (AI-based)")
@RestController
@RequestMapping("/reviews")
@RequiredArgsConstructor
public class ReviewController {

    private final ReviewService reviewService;

    @Operation(summary = "Review a submission (AI code review)")
    @PostMapping("/submission/{submissionId}")
    public ApiResponse<ReviewResponse> review(
            @Parameter(description = "Submission ID")
            @PathVariable UUID submissionId
    ) {
        return ApiResponse.success(
                reviewService.reviewSubmission(submissionId)
        );
    }

    @Operation(summary = "Get review history of a submission")
    @GetMapping("/submission/{submissionId}")
    public ApiResponse<List<ReviewResponse>> history(
            @Parameter(description = "Submission ID")
            @PathVariable UUID submissionId
    ) {
        return ApiResponse.success(
                reviewService.getSubmissionReviews(submissionId)
        );
    }
}