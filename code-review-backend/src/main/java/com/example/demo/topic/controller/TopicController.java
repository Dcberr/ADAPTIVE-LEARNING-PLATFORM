package com.example.demo.topic.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicResponse;
import com.example.demo.topic.service.TopicService;

@RestController
@RequestMapping("/topics")
@RequiredArgsConstructor
public class TopicController {

    private final TopicService topicService;

    @PostMapping
    public ApiResponse<TopicResponse> createTopic(
            @RequestBody CreateTopicRequest request
    ) {

        return ApiResponse.success(
                topicService.createTopic(request)
        );
    }

    @GetMapping("/class/{classId}")
    public ApiResponse<List<TopicResponse>> getTopicsByClass(
            @PathVariable UUID classId
    ) {

        return ApiResponse.success(
                topicService.getTopicsByClass(classId)
        );
    }
}