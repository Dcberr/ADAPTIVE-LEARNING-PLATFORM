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
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.service.ProblemService;

@Service
@RequiredArgsConstructor
public class AssignmentServiceImpl implements AssignmentService {

    private final AssignmentRepository assignmentRepository;
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final ProblemService problemService;

    @Override
    public AssignmentResponse createAssignment(CreateAssignmentRequest request) {

        Assignment assignment = Assignment.builder()
                .topicId(request.getTopicId())
                .title(request.getTitle())
                // .description(request.getDescription())
                .deadline(request.getDeadline())
                .createdAt(Instant.now())
                .difficulty(request.getDifficulty())
                .status(AssignmentStatus.PENDING)
                .build();

        assignmentRepository.save(assignment);

        CreateAssignmentRequest.ProblemRequest problemReq = request.getProblem();

        ProblemResponse problem = problemService.createProblem(
                CreateProblemRequest.builder()
                        .description(problemReq.getDescription())
                        .assignmentId(assignment.getId())
                        .testcases(problemReq.getTestcases())
                        .build()
        );

        assignmentProblemRepository.save(
            AssignmentProblem.builder()
                .assignmentId(assignment.getId())
                .problemId(problem.getId())
                .build()
        );

        return mapAssignment(assignment);
    }

    @Override
    public List<AssignmentResponse> getAssignmentsByTopic(UUID topicId) {

        return assignmentRepository.findByTopicId(topicId)
                .stream()
                .map(this::mapAssignment)
                .toList();
    }

    private AssignmentResponse mapAssignment(Assignment assignment) {
        return AssignmentResponse.builder()
                .id(assignment.getId())
                .title(assignment.getTitle())
                .deadline(assignment.getDeadline())
                .difficulty(assignment.getDifficulty())
                .status(assignment.getStatus())
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