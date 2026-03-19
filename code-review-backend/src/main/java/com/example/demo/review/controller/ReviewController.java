package com.example.demo.review.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.review.dto.ReviewResponse;
import com.example.demo.review.service.ReviewService;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/reviews")
@RequiredArgsConstructor
public class ReviewController {

    private final ReviewService reviewService;

    @PostMapping("/submission/{submissionId}")
    public ApiResponse<ReviewResponse> review(
            @PathVariable UUID submissionId
    ) {

        return ApiResponse.success(
                reviewService.reviewSubmission(submissionId)
        );
    }

    @GetMapping("/submission/{submissionId}")
    public ApiResponse<List<ReviewResponse>> history(
            @PathVariable UUID submissionId
    ) {

        return ApiResponse.success(
                reviewService.getSubmissionReviews(submissionId)
        );
    }
}