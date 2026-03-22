package com.example.demo.review.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.review.entity.CodeReview;

import java.util.List;
import java.util.UUID;

public interface CodeReviewRepository
        extends JpaRepository<CodeReview, UUID> {

    List<CodeReview> findBySubmissionId(UUID submissionId);

}