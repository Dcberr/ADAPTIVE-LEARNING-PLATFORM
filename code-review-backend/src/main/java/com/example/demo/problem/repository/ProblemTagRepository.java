package com.example.demo.problem.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.problem.entity.ProblemTag;

@Repository
public interface ProblemTagRepository extends JpaRepository<ProblemTag, UUID> {

    List<ProblemTag> findByProblemId(UUID problemId);

    void deleteByProblemId(UUID problemId);
}
