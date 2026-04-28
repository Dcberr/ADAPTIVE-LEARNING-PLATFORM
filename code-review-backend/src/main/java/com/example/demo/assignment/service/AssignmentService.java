package com.example.demo.assignment.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;


public interface AssignmentService {

    AssignmentResponse createAssignment(CreateAssignmentRequest request);

    List<AssignmentResponse> getAssignmentsByTopic(UUID topicId);

    public AssignmentResponse updateAssignment(UUID assignmentId, UpdateAssignmentRequest request);

    void addProblemToAssignment(UUID assignmentId, UUID problemId);

    AssignmentResponse addLeetCodeProblemToAssignment(UUID topicId, UUID assignmentId, UUID problemId);

}
