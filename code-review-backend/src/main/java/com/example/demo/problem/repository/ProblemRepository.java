package com.example.demo.problem.repository;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.problem.entity.Problem;

@Repository
public interface ProblemRepository
        extends JpaRepository<Problem, UUID> {
        boolean existsBySourceAndExternalId(String source, String externalId);

        Optional<Problem> findBySourceAndExternalId(String source, String externalId);

}
