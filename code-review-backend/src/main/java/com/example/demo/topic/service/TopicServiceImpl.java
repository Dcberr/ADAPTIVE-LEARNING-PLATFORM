package com.example.demo.topic.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.assignment.dto.AssignmentOverviewResponse;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.assignment.service.AssignmentService;
import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.classmanagement.repository.ClassRepository;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.service.DocumentService;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.topic.dto.AddLeetCodeProblemToTopicRequest;
import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicDetailResponse;
import com.example.demo.topic.dto.TopicOverviewResponse;
import com.example.demo.topic.dto.TopicResponse;
import com.example.demo.topic.dto.UpdateTopicRequest;
import com.example.demo.topic.entity.Topic;
import com.example.demo.topic.repository.TopicRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TopicServiceImpl implements TopicService {

    private final TopicRepository topicRepository;
    private final AssignmentRepository assignmentRepository;
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final ProblemRepository problemRepository;
    private final AssignmentService assignmentService;
    private final DocumentService documentService;
    private final ClassRepository classRepository;

    @Override
    public TopicResponse createTopic(CreateTopicRequest req) {
        classRepository.findByIdAndDeletedAtIsNull(req.getClassId())
                .orElseThrow(() -> new AppException(ErrorCode.CLASS_NOT_FOUND));

        Topic topic = Topic.builder()
                .classId(req.getClassId())
                .title(req.getTitle())
                .description(req.getDescription())
                .createdAt(Instant.now())
                .build();

        topicRepository.save(topic);

        return map(topic);
    }

    @Override
    public TopicResponse updateTopic(UUID topicId, UpdateTopicRequest req) {
        Topic topic = getActiveTopic(topicId);

        if (req.getTitle() != null) {
            topic.setTitle(req.getTitle());
        }
        if (req.getDescription() != null) {
            topic.setDescription(req.getDescription());
        }

        topicRepository.save(topic);
        return map(topic);
    }

    @Override
    public List<TopicResponse> getTopicsByClass(UUID classId) {

        classRepository.findByIdAndDeletedAtIsNull(classId)
                .orElseThrow(() -> new AppException(ErrorCode.CLASS_NOT_FOUND));

        return topicRepository.findByClassIdAndDeletedAtIsNull(classId)
                .stream()
                .map(this::map)
                .toList();
    }

    private TopicResponse map(Topic topic) {

        return TopicResponse.builder()
                .id(topic.getId())
                .classId(topic.getClassId())
                .title(topic.getTitle())
                .description(topic.getDescription())
                .build();
    }

    @Override
    public TopicDetailResponse getTopicDetail(UUID topicId) {

        Topic topic = getActiveTopic(topicId);

        List<AssignmentOverviewResponse> assignments = assignmentService.getAssignmentsByTopic(topicId);

        List<DocumentResponse> documents = documentService.getDocumentsByTopic(topicId);

        return TopicDetailResponse.builder()
                .id(topic.getId())
                .title(topic.getTitle())
                .description(topic.getDescription())
                .assignments(assignments)
                .documents(documents)
                .build();
    }

    @Override
    public TopicOverviewResponse getTopicOverviewByClassId(UUID classId) {

        classRepository.findByIdAndDeletedAtIsNull(classId)
                .orElseThrow(() -> new AppException(ErrorCode.CLASS_NOT_FOUND));

        List<Topic> topics = topicRepository.findByClassIdAndDeletedAtIsNull(classId);

        return TopicOverviewResponse.builder()
                .ids(topics.stream().map(Topic::getId).toList())
                .build();
    }

    @Override
    public AssignmentResponse addLeetCodeProblemToTopic(UUID topicId, AddLeetCodeProblemToTopicRequest request) {

        Topic topic = getActiveTopic(topicId);

        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new AppException(ErrorCode.PROBLEM_NOT_FOUND));

        if (problem.getType() != ProblemType.LIBRARY || !"LEETCODE".equals(problem.getSource())) {
            throw new AppException(ErrorCode.VALIDATION_ERROR);
        }

        Assignment assignment = Assignment.builder()
                .topicId(topic.getId())
                .title(resolveAssignmentTitle(request, problem))
                .startTime(request.getStartTime())
                .deadline(request.getDeadline())
                .timeLimit(request.getTimeLimit())
                .maxScore(request.getMaxScore())
                .maxSubmission(request.getMaxSubmission())
                .tags(request.getTags())
                .createdAt(Instant.now())
                .difficulty(resolveDifficulty(problem.getDifficulty()))
                .status(AssignmentStatus.PENDING)
                .build();

        assignmentRepository.save(assignment);

        assignmentProblemRepository.save(
                AssignmentProblem.builder()
                        .assignmentId(assignment.getId())
                        .problemId(problem.getId())
                        .build()
        );

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
    public void deleteTopic(UUID topicId) {
        Topic topic = getActiveTopic(topicId);
        topic.setDeletedAt(Instant.now());
        topicRepository.save(topic);
    }

    private String resolveAssignmentTitle(AddLeetCodeProblemToTopicRequest request, Problem problem) {
        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            return request.getTitle();
        }
        return problem.getTitle();
    }

    private AssigmentDifficulty resolveDifficulty(String difficulty) {
        if (difficulty == null || difficulty.isBlank()) {
            return AssigmentDifficulty.MEDIUM;
        }

        try {
            return AssigmentDifficulty.valueOf(difficulty.toUpperCase());
        } catch (IllegalArgumentException ex) {
            return AssigmentDifficulty.MEDIUM;
        }
    }

    private Topic getActiveTopic(UUID topicId) {
        return topicRepository.findByIdAndDeletedAtIsNull(topicId)
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));
    }

}
