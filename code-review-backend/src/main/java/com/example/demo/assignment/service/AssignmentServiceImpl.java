package com.example.demo.assignment.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;

@Service
@RequiredArgsConstructor
public class AssignmentServiceImpl implements AssignmentService {

    private final AssignmentRepository assignmentRepository;
    private final AssignmentProblemRepository assignmentProblemRepository;

    @Override
    public AssignmentResponse createAssignment(CreateAssignmentRequest request) {

        Assignment assignment = Assignment.builder()
                .topicId(request.getTopicId())
                .title(request.getTitle())
                .description(request.getDescription())
                .deadline(request.getDeadline())
                .createdAt(Instant.now())
                .build();

        assignmentRepository.save(assignment);

        return map(assignment);
    }

    @Override
    public List<AssignmentResponse> getAssignmentsByTopic(UUID topicId) {

        return assignmentRepository.findByTopicId(topicId)
                .stream()
                .map(this::map)
                .toList();
    }

    private AssignmentResponse map(Assignment assignment) {

        return AssignmentResponse.builder()
                .id(assignment.getId())
                .topicId(assignment.getTopicId())
                .title(assignment.getTitle())
                .description(assignment.getDescription())
                .deadline(assignment.getDeadline())
                .build();
    }

    @Override
    public void addProblemToAssignment(UUID assignmentId, UUID problemId) {

        AssignmentProblem mapping =
                AssignmentProblem.builder()
                        .assignmentId(assignmentId)
                        .problemId(problemId)
                        .build();

        assignmentProblemRepository.save(mapping);
    }
}