package com.example.demo.assignment.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.assignment.entity.AssignmentProblem;

@Repository
public interface AssignmentProblemRepository
        extends JpaRepository<AssignmentProblem, UUID> {

    AssignmentProblem findByAssignmentId(UUID assignmentId);
    AssignmentProblem findByProblemId(UUID problemId);
    boolean existsByAssignmentIdAndProblemId(UUID assignmentId, UUID problemId);

}
