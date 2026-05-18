package com.example.demo.review.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.review.dto.ReviewResponse;

public interface ReviewService {

    ReviewResponse reviewSubmission(UUID submissionId, UUID requesterId);

    List<ReviewResponse> getSubmissionReviews(UUID submissionId);

    List<ReviewResponse> getSubmissionReviewsByUser(UUID submissionId, UUID userId);

    ReviewResponse reviewCode(UUID problemId, UUID submissionId, String code, String language, UUID userId);

    List<ReviewResponse> getProblemReviews(UUID problemId);

    List<ReviewResponse> getProblemReviewsByUser(UUID problemId, UUID userId);

    List<ReviewResponse> getAllReviewsForUser(UUID userId);

    List<ReviewResponse> getReviewByUserIdAndProblemId(UUID userId, UUID problemId);

}
