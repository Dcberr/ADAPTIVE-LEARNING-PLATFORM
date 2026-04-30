package com.example.demo.assignment.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.AddProblemToAssignmentRequest;
import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.service.AssignmentService;
import com.example.demo.common.response.ApiResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/assignments")
@RequiredArgsConstructor
@Tag(name = "Assignment", description = "APIs for managing assignments")
public class AssignmentController {

    private final AssignmentService assignmentService;

    @PostMapping
    @Operation(summary = "Create new assignment")
    public ApiResponse<AssignmentResponse> createAssignment(
            @RequestBody CreateAssignmentRequest request
    ) {

        return ApiResponse.success(
                assignmentService.createAssignment(request)
        );
    }

    @Operation(summary = "Get assignments by topicId")
    @GetMapping("/topic/{topicId}")
    public ApiResponse<List<AssignmentResponse>> getAssignments(
            @PathVariable UUID topicId
    ) {

        return ApiResponse.success(
                assignmentService.getAssignmentsByTopic(topicId)
        );
    }

    @Operation(summary = "Add an existing LeetCode problem to an assignment in a topic")
    @PostMapping("/topic/{topicId}/{assignmentId}/problems/leetcode")
    public ApiResponse<AssignmentResponse> addLeetCodeProblemToAssignment(
            @PathVariable UUID topicId,
            @PathVariable UUID assignmentId,
            @RequestBody AddProblemToAssignmentRequest request
    ) {
        return ApiResponse.success(
                assignmentService.addLeetCodeProblemToAssignment(
                        topicId,
                        assignmentId,
                        request.getProblemId()
                )
        );
    }
}
