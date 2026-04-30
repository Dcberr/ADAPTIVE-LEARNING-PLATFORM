package com.example.demo.topic.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.topic.dto.AddLeetCodeProblemToTopicRequest;
import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicDetailResponse;
import com.example.demo.topic.dto.TopicOverviewResponse;
import com.example.demo.topic.dto.TopicResponse;

public interface TopicService {

    TopicResponse createTopic(CreateTopicRequest request);

    List<TopicResponse> getTopicsByClass(UUID classId);

    public TopicDetailResponse getTopicDetail(UUID topicId);
    
    public TopicOverviewResponse getTopicOverviewByClassId(UUID classId);   

    AssignmentResponse addLeetCodeProblemToTopic(UUID topicId, AddLeetCodeProblemToTopicRequest request);

}
