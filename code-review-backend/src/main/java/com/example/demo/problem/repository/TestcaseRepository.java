package com.example.demo.problem.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.problem.entity.Testcase;

@Repository
public interface TestcaseRepository
        extends JpaRepository<Testcase, UUID> {

    List<Testcase> findByProblemId(UUID problemId);

}
