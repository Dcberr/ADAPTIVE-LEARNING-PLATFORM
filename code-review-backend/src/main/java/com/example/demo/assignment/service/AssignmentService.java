package com.example.demo.assignment.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.dto.CreateAssignmentRequest;


public interface AssignmentService {

    AssignmentResponse createAssignment(CreateAssignmentRequest request);

    List<AssignmentResponse> getAssignmentsByTopic(UUID topicId);

    void addProblemToAssignment(UUID assignmentId, UUID problemId);

}