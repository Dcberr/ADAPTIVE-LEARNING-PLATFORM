package com.example.demo.topic.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicResponse;

public interface TopicService {

    TopicResponse createTopic(CreateTopicRequest request);

    List<TopicResponse> getTopicsByClass(UUID classId);

}
