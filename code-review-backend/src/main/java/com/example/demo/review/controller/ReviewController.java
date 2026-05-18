package com.example.demo.review.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.review.dto.ReviewResponse;
import com.example.demo.review.service.ReviewService;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.List;
import java.util.UUID;

import org.springframework.security.core.Authentication;

import com.example.demo.review.dto.ReviewCodeRequest;

@Tag(name = "Review", description = "APIs for code review (AI-based)")
@RestController
@RequestMapping("/reviews")
@RequiredArgsConstructor
public class ReviewController {

    private final ReviewService reviewService;

    @Operation(summary = "Review a submission (AI code review)")
    @Hidden
    @PostMapping("/submission/{submissionId}")
    public ApiResponse<ReviewResponse> review(
            Authentication auth,
            @Parameter(description = "Submission ID")
            @PathVariable UUID submissionId
    ) {
        UUID userId = (UUID) auth.getPrincipal();
        return ApiResponse.success(
                reviewService.reviewSubmission(submissionId, userId)
        );
    }

//     @Operation(summary = "Get review history of a submission")
//     @GetMapping("/submission/{submissionId}")
//     public ApiResponse<List<ReviewResponse>> history(
//             Authentication auth,
//             @Parameter(description = "Submission ID")
//             @PathVariable UUID submissionId
//     ) {
//         UUID userId = (UUID) auth.getPrincipal();
//         return ApiResponse.success(
//                 reviewService.getSubmissionReviewsByUser(submissionId, userId)
//         );
//     }

    @Operation(summary = "Review code directly without submission")
    @PostMapping("/code")
    public ApiResponse<ReviewResponse> reviewCode(
            Authentication auth,
            @RequestBody ReviewCodeRequest request
    ) {
        UUID userId = (UUID) auth.getPrincipal();
        return ApiResponse.success(
                reviewService.reviewCode(
                        request.getProblemId(),
                        request.getSubmissionId(),
                        request.getCode(),
                        request.getLanguage(),
                        userId
                )
        ); 
    }

    @Operation(summary = "Get all reviews for a problem")
    @GetMapping("/problem/{problemId}/me")
    public ApiResponse<List<ReviewResponse>> getProblemReviews(
            Authentication auth,
            @Parameter(description = "Problem ID")
            @PathVariable UUID problemId
    ) {
        UUID userId = (UUID) auth.getPrincipal();
        return ApiResponse.success(
                reviewService.getProblemReviewsByUser(problemId, userId)
        );
    }

    @Operation(summary = "Get all reviews for a problem by user")
        @GetMapping("/problem/{problemId}/user/{userId}")
        public ApiResponse<List<ReviewResponse>> getProblemReviewsByUser(
                @Parameter(description = "Problem ID")
                @PathVariable UUID problemId,
                @Parameter(description = "User ID")
                @PathVariable UUID userId
        ) {
            return ApiResponse.success(
                    reviewService.getProblemReviewsByUser(problemId, userId)
            );
        }

//     @Operation(summary = "Get all reviews (instructor only)")
//     @GetMapping("/all")
//     public ApiResponse<List<ReviewResponse>> getAllReviews(
//             Authentication auth
//     ) {
//         UUID userId = (UUID) auth.getPrincipal();
//         return ApiResponse.success(
//                 reviewService.getAllReviewsForUser(userId)
//         );
//     }

}
    
