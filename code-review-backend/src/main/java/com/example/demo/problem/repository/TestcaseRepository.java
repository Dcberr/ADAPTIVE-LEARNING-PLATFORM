package com.example.demo.problem.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.demo.problem.entity.Testcase;

@Repository
public interface TestcaseRepository
        extends JpaRepository<Testcase, UUID> {

    List<Testcase> findByProblemId(UUID problemId);


    @Query("""
            SELECT t FROM Testcase t
            JOIN AssignmentProblem ap ON t.problemId = ap.problemId
            WHERE ap.assignmentId = :assignmentId 
            """)
    List<Testcase> findByAssignmentId(UUID assignmentId);

}
