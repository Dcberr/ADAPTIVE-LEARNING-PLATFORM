package com.example.demo.problem.repository;

import java.util.Optional;
import java.util.Collection;
import java.util.UUID;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;

@Repository
public interface ProblemRepository
        extends JpaRepository<Problem, UUID>, JpaSpecificationExecutor<Problem> {
        boolean existsBySourceAndExternalId(String source, String externalId);

        Optional<Problem> findBySourceAndExternalId(String source, String externalId);

        Collection<Problem> findAllBySourceAndExternalIdIn(String source, Collection<String> externalIds);

        Optional<Problem> findByIdAndDeletedAtIsNull(UUID id);

        Page<Problem> findAllByTypeAndDeletedAtIsNullOrderByCreatedAtDesc(ProblemType type, Pageable pageable);

}
