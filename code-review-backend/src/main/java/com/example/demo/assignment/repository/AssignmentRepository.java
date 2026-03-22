package com.example.demo.assignment.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.assignment.entity.Assignment;

@Repository
public interface AssignmentRepository
        extends JpaRepository<Assignment, UUID> {

    List<Assignment> findByTopicId(UUID topicId);
    // Assignment findByProblemId(UUID problemId);

}
