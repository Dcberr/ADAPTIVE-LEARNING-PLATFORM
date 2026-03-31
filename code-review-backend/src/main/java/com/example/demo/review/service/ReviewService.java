package com.example.demo.review.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.review.dto.ReviewResponse;

public interface ReviewService {

    ReviewResponse reviewSubmission(UUID submissionId);

    List<ReviewResponse> getSubmissionReviews(UUID submissionId);

}