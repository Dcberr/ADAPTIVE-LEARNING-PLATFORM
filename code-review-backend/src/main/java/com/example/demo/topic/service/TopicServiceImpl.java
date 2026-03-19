package com.example.demo.topic.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicResponse;
import com.example.demo.topic.entity.Topic;
import com.example.demo.topic.repository.TopicRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TopicServiceImpl implements TopicService {

    private final TopicRepository topicRepository;

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
}
