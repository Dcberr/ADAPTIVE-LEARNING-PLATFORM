package com.example.demo.assignment.service;

import java.time.Instant;
import java.util.Map;
import java.util.List;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;
import com.example.demo.assignment.dto.AssignmentDeadlineResponse;
import com.example.demo.assignment.dto.AssignmentDetailResponse;
import com.example.demo.assignment.dto.AssignmentOverviewResponse;
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
import com.example.demo.problem.dto.TestcaseDto;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.service.ProblemService;
import com.example.demo.submission.repository.SubmissionRepository;
import com.example.demo.topic.entity.Topic;
import com.example.demo.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
public class AssignmentServiceImpl implements AssignmentService {

    private final AssignmentRepository assignmentRepository;
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;
    private final ProblemService problemService;
    private final SubmissionRepository submissionRepository;
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
                        .saveToLibrary(problemReq.isSaveToLibrary())
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
    public List<AssignmentOverviewResponse> getAssignmentsByTopic(UUID topicId, UUID userId) {
        topicRepository.findByIdAndDeletedAtIsNull(topicId)
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));

        return assignmentRepository.findByTopicIdAndDeletedAtIsNull(topicId)
                .stream()
                .map(this::mapAssignmentOverview)
                .toList();
    }

    @Override
    public List<AssignmentDeadlineResponse> getAssignmentDeadlines() {
        List<Assignment> assignments = assignmentRepository.findByDeletedAtIsNullOrderByDeadlineAsc();

        Map<UUID, Topic> topicsById = topicRepository.findAllById(
                assignments.stream()
                        .map(Assignment::getTopicId)
                        .distinct()
                        .toList())
                .stream()
                .collect(Collectors.toMap(Topic::getId, Function.identity()));

        return assignments.stream()
                .map(assignment -> mapAssignmentDeadline(assignment, topicsById.get(assignment.getTopicId())))
                .toList();
    }

    @Override
    public AssignmentDetailResponse getAssignmentById(UUID assignmentId, UUID userId) {
        return mapAssignmentDetail(getActiveAssignment(assignmentId), userId);
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
        return mapAssignment(assignment, null);
    }

    private AssignmentResponse mapAssignment(Assignment assignment, UUID userId) {
        Integer attemptsUsed = resolveAttemptsUsed(assignment, userId);
        Integer remainingSubmission = resolveRemainingSubmission(assignment, attemptsUsed);
        return AssignmentResponse.builder()
                .id(assignment.getId())
                .title(assignment.getTitle())
                .deadline(assignment.getDeadline())
                .difficulty(assignment.getDifficulty())
                .startTime(assignment.getStartTime())
                .timeLimit(assignment.getTimeLimit())
                .maxScore(assignment.getMaxScore())
                .maxSubmission(assignment.getMaxSubmission())
                .attemptsUsed(attemptsUsed)
                .remainingSubmission(remainingSubmission)
                .tags(assignment.getTags())
                .status(assignment.getStatus())
                .build();
    }

    private AssignmentOverviewResponse mapAssignmentOverview(Assignment assignment) {
        return AssignmentOverviewResponse.builder()
                .id(assignment.getId())
                .title(assignment.getTitle())
                .build();
    }

    private AssignmentDeadlineResponse mapAssignmentDeadline(Assignment assignment, Topic topic) {
        return AssignmentDeadlineResponse.builder()
                .id(assignment.getId())
                .topicId(assignment.getTopicId())
                .topicTitle(topic != null ? topic.getTitle() : null)
                .title(assignment.getTitle())
                .startTime(assignment.getStartTime())
                .deadline(assignment.getDeadline())
                .difficulty(assignment.getDifficulty())
                .status(assignment.getStatus())
                .build();
    }

    private AssignmentDetailResponse mapAssignmentDetail(Assignment assignment, UUID userId) {
        Integer attemptsUsed = resolveAttemptsUsed(assignment, userId);
        Integer remainingSubmission = resolveRemainingSubmission(assignment, attemptsUsed);
        return AssignmentDetailResponse.builder()
                .id(assignment.getId())
                .title(assignment.getTitle())
                .deadline(assignment.getDeadline())
                .difficulty(assignment.getDifficulty())
                .startTime(assignment.getStartTime())
                .timeLimit(assignment.getTimeLimit())
                .maxScore(assignment.getMaxScore())
                .maxSubmission(assignment.getMaxSubmission())
                .attemptsUsed(attemptsUsed)
                .remainingSubmission(remainingSubmission)
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
    public AssignmentResponse addLibraryProblemToAssignment(UUID topicId, UUID assignmentId, UUID problemId) {

        Assignment assignment = getActiveAssignment(assignmentId);

        if (!assignment.getTopicId().equals(topicId)) {
            throw new AppException(ErrorCode.ASSIGNMENT_NOT_FOUND);
        }

        Problem problem = problemRepository.findById(problemId)
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        if (problem.getType() != ProblemType.LIBRARY || !"LEETCODE".equals(problem.getSource())) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        ProblemResponse clonedProblem = cloneLibraryProblemForAssignment(assignment, problem);

        if (!assignmentProblemRepository.existsByAssignmentIdAndProblemId(assignmentId, clonedProblem.getId())) {
            assignmentProblemRepository.save(
                    AssignmentProblem.builder()
                            .assignmentId(assignmentId)
                            .problemId(clonedProblem.getId())
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

    private Integer resolveAttemptsUsed(Assignment assignment, UUID userId) {
        if (userId == null) {
            return null;
        }
        return Math.toIntExact(submissionRepository.countByUserIdAndAssignmentId(userId, assignment.getId()));
    }

    private Integer resolveRemainingSubmission(Assignment assignment, Integer attemptsUsed) {
        if (attemptsUsed == null) {
            return null;
        }
        int maxSubmission = assignment.getMaxSubmission();
        if (maxSubmission <= 0) {
            return null;
        }
        return Math.max(maxSubmission - attemptsUsed, 0);
    }

    private ProblemResponse cloneLibraryProblemForAssignment(Assignment assignment, Problem libraryProblem) {
        List<TestcaseDto> clonedTestcases = testcaseRepository.findByProblemId(libraryProblem.getId()).stream()
                .map(this::toTestcaseDto)
                .toList();

        return problemService.createManualProblem(
                CreateProblemRequest.builder()
                        .title(libraryProblem.getTitle())
                        .description(libraryProblem.getDescription())
                        .difficulty(libraryProblem.getDifficulty())
                        .assignmentId(assignment.getId())
                        .problemConstraint(libraryProblem.getProblemConstraint())
                        .starterCodes(libraryProblem.getStarterCodes())
                        .testcases(clonedTestcases)
                        .saveToLibrary(false)
                        .build());
    }

    private TestcaseDto toTestcaseDto(Testcase testcase) {
        return TestcaseDto.builder()
                .input(testcase.getInput())
                .expectedOutput(testcase.getExpectedOutput())
                .isHidden(testcase.isHidden())
                .ignoreOrder(testcase.isIgnoreOrder())
                .explanation(testcase.getExplanation())
                .build();
    }
}
