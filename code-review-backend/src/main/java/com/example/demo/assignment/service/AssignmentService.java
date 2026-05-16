package com.example.demo.assignment.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.dto.AssignmentDeadlineResponse;
import com.example.demo.assignment.dto.AssignmentDetailResponse;
import com.example.demo.assignment.dto.AssignmentOverviewResponse;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;


public interface AssignmentService {

    AssignmentResponse createAssignment(CreateAssignmentRequest request);

    List<AssignmentOverviewResponse> getAssignmentsByTopic(UUID topicId, UUID userId);

    List<AssignmentDeadlineResponse> getAssignmentDeadlines(UUID userId);

    AssignmentDetailResponse getAssignmentById(UUID assignmentId, UUID userId);

    public AssignmentResponse updateAssignment(UUID assignmentId, UpdateAssignmentRequest request);

    void addProblemToAssignment(UUID assignmentId, UUID problemId);

    AssignmentResponse addLibraryProblemToAssignment(UUID topicId, UUID assignmentId, UUID problemId);

    void deleteAssignment(UUID assignmentId);

}
