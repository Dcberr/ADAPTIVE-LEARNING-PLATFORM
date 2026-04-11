package com.example.demo.assignment.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.mapper.AssignmentMapper;
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
    private final AssignmentMapper assignmentMapper;

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
                        .problemConstraint(problemReq.getProblemConstraint())
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

    @Override
    public AssignmentResponse updateAssignment(UUID assignmentId, UpdateAssignmentRequest request) {

        Assignment assignment = assignmentRepository.findById(assignmentId)
                .orElseThrow(() -> new RuntimeException("Assignment not found"));

        assignmentMapper.updateAssignmentFromDto(request, assignment);

        assignmentRepository.save(assignment);

        return mapAssignment(assignment);
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