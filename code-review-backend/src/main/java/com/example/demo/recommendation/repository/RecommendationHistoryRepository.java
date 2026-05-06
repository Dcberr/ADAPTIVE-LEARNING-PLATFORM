package com.example.demo.recommendation.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.recommendation.entity.RecommendationHistory;

public interface RecommendationHistoryRepository extends JpaRepository<RecommendationHistory, UUID> {

    List<RecommendationHistory> findByStudentIdOrderByCreatedAtDesc(UUID studentId);

    List<RecommendationHistory> findByStudentIdAndProblemIdOrderByCreatedAtDesc(UUID studentId, UUID problemId);
}
