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
import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.service.ProblemService;
import com.example.demo.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
public class AssignmentServiceImpl implements AssignmentService {

    private final AssignmentRepository assignmentRepository;
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final ProblemRepository problemRepository;
    private final ProblemService problemService;
    private final AssignmentMapper assignmentMapper;
    private final TopicRepository topicRepository;

    @Override
    public AssignmentResponse createAssignment(CreateAssignmentRequest request) {
        topicRepository.findByIdAndDeletedAtIsNull(request.getTopicId())
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));

        Assignment assignment = Assignment.builder()
                .topicId(request.getTopicId())
                .title(request.getTitle())
                // .description(request.getDescription())
                .deadline(request.getDeadline())
                .startTime(request.getStartTime())
                .timeLimit(request.getTimeLimit())
                .maxScore(request.getMaxScore())
                .maxSubmission(request.getMaxSubmission())
                .tags(request.getTags())
                .createdAt(Instant.now())
                .difficulty(request.getDifficulty())
                .status(AssignmentStatus.PENDING)
                .build();

        assignmentRepository.save(assignment);

        CreateAssignmentRequest.ProblemRequest problemReq = request.getProblem();

        ProblemResponse problem = problemService.createManualProblem(
                CreateProblemRequest.builder()
                        .description(problemReq.getDescription())
                        .assignmentId(assignment.getId())
                        .starterCodes(problemReq.getStarterCodes())
                        // .leetCodeCodeSnippet(problemReq.getLeetCodeCodeSnippet())
                        // .leetCodeLanguage(problemReq.getLeetCodeLanguage())
                        .problemConstraint(problemReq.getProblemConstraint())
                        .testcases(problemReq.getTestcases())
                        .title(assignment.getTitle())
                        .difficulty(assignment.getDifficulty().toString())
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
        topicRepository.findByIdAndDeletedAtIsNull(topicId)
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));

        return assignmentRepository.findByTopicIdAndDeletedAtIsNull(topicId)
                .stream()
                .map(this::mapAssignment)
                .toList();
    }

    @Override
    public AssignmentResponse getAssignmentById(UUID assignmentId) {
        return mapAssignment(getActiveAssignment(assignmentId));
    }

    @Override
    public AssignmentResponse updateAssignment(UUID assignmentId, UpdateAssignmentRequest request) {

        Assignment assignment = getActiveAssignment(assignmentId);

        if (request.getTopicId() != null) {
            topicRepository.findByIdAndDeletedAtIsNull(request.getTopicId())
                    .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));
        }

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
                .startTime(assignment.getStartTime())
                .timeLimit(assignment.getTimeLimit())
                .maxScore(assignment.getMaxScore())
                .maxSubmission(assignment.getMaxSubmission())
                .tags(assignment.getTags())
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

    @Override
    public AssignmentResponse addLeetCodeProblemToAssignment(UUID topicId, UUID assignmentId, UUID problemId) {

        Assignment assignment = getActiveAssignment(assignmentId);

        if (!assignment.getTopicId().equals(topicId)) {
            throw new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND);
        }

        Problem problem = problemRepository.findById(problemId)
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        if (problem.getType() != ProblemType.LEETCODE || !"LEETCODE".equals(problem.getSource())) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        if (!assignmentProblemRepository.existsByAssignmentIdAndProblemId(assignmentId, problemId)) {
            assignmentProblemRepository.save(
                    AssignmentProblem.builder()
                            .assignmentId(assignmentId)
                            .problemId(problemId)
                            .build()
            );
        }

        return mapAssignment(assignment);
    }

    @Override
    public void deleteAssignment(UUID assignmentId) {
        Assignment assignment = getActiveAssignment(assignmentId);
        assignment.setDeletedAt(Instant.now());
        assignmentRepository.save(assignment);
    }

    private Assignment getActiveAssignment(UUID assignmentId) {
        return assignmentRepository.findByIdAndDeletedAtIsNull(assignmentId)
                .orElseThrow(() -> new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND));
    }
}
