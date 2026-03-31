package com.example.demo.assignment.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.assignment.entity.AssignmentProblem;

@Repository
public interface AssignmentProblemRepository
        extends JpaRepository<AssignmentProblem, UUID> {

    List<AssignmentProblem> findByAssignmentId(UUID assignmentId);

}
