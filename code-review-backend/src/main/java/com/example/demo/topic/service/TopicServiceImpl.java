package com.example.demo.topic.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.assignment.service.AssignmentService;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.entity.Document;
import com.example.demo.document.repository.DocumentRepository;
import com.example.demo.document.service.DocumentService;
import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicDetailResponse;
import com.example.demo.topic.dto.TopicOverviewResponse;
import com.example.demo.topic.dto.TopicResponse;
import com.example.demo.topic.entity.Topic;
import com.example.demo.topic.repository.TopicRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TopicServiceImpl implements TopicService {

    private final TopicRepository topicRepository;
//     private final AssignmentRepository assignmentRepository;
//     private final DocumentRepository documentRepository;
    private final AssignmentService assignmentService;
    private final DocumentService documentService;   

    @Override
    public TopicResponse createTopic(CreateTopicRequest req) {

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
    public List<TopicResponse> getTopicsByClass(UUID classId) {

        return topicRepository.findByClassId(classId)
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

        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found"));

        List<AssignmentResponse> assignments = assignmentService.getAssignmentsByTopic(topicId);

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

        List<Topic> topics = topicRepository.findByClassId(classId);

        return TopicOverviewResponse.builder()
                .ids(topics.stream().map(Topic::getId).toList())
                .build();
    }

}
