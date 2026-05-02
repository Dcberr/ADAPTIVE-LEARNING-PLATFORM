package com.example.demo.assignment.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.assignment.entity.Assignment;

@Repository
public interface AssignmentRepository
        extends JpaRepository<Assignment, UUID> {

    List<Assignment> findByTopicIdAndDeletedAtIsNull(UUID topicId);

    java.util.Optional<Assignment> findByIdAndDeletedAtIsNull(UUID id);
    // Assignment findByProblemId(UUID problemId);

}
