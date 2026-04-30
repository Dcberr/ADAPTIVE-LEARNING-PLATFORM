package com.example.demo.topic.controller;

import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.common.response.ApiResponse;
import com.example.demo.topic.dto.AddLeetCodeProblemToTopicRequest;
import com.example.demo.topic.dto.CreateTopicRequest;
import com.example.demo.topic.dto.TopicDetailResponse;
import com.example.demo.topic.dto.TopicOverviewResponse;
import com.example.demo.topic.dto.TopicResponse;
import com.example.demo.topic.service.TopicService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Topic", description = "APIs for topic management")
@RestController
@RequestMapping("/topics")
@RequiredArgsConstructor
public class TopicController {

    private final TopicService topicService;

    @Operation(summary = "Create a new topic")
    @PostMapping
    public ApiResponse<TopicResponse> createTopic(
            @RequestBody CreateTopicRequest request
    ) {
        return ApiResponse.success(
                topicService.createTopic(request)
        );
    }

    @Operation(summary = "Get topics overview by classId")
    @GetMapping("/class/{classId}")
    public ApiResponse<TopicOverviewResponse> getTopicsByClass(
            @Parameter(description = "Class ID")
            @PathVariable UUID classId
    ) {
        return ApiResponse.success(
                topicService.getTopicOverviewByClassId(classId)
        );
    }

    @Operation(summary = "Get topic detail (assignments + documents)")
    @GetMapping("/{topicId}")
    public ApiResponse<TopicDetailResponse> getTopicDetail(
            @Parameter(description = "Topic ID")
            @PathVariable UUID topicId
    ) {
        return ApiResponse.success(
                topicService.getTopicDetail(topicId)
        );
    }

    @Operation(summary = "Add an existing LeetCode problem to a topic")
    @PostMapping("/{topicId}/assignments/leetcode")
    public ApiResponse<AssignmentResponse> addLeetCodeProblemToTopic(
            @Parameter(description = "Topic ID")
            @PathVariable UUID topicId,
            @RequestBody AddLeetCodeProblemToTopicRequest request
    ) {
        return ApiResponse.success(
                topicService.addLeetCodeProblemToTopic(topicId, request)
        );
    }
}
