package com.example.demo.assignment.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.dto.AddProblemToAssignmentRequest;
import com.example.demo.assignment.dto.AssignmentDetailResponse;
import com.example.demo.assignment.dto.AssignmentOverviewResponse;
import com.example.demo.assignment.dto.AssignmentResponse;
import com.example.demo.assignment.dto.CreateAssignmentRequest;
import com.example.demo.assignment.dto.UpdateAssignmentRequest;
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

    @Operation(summary = "Get assignment overview by topicId")
    @GetMapping("/topic/{topicId}")
    public ApiResponse<List<AssignmentOverviewResponse>> getAssignments(
            @PathVariable UUID topicId
    ) {

        return ApiResponse.success(
                assignmentService.getAssignmentsByTopic(topicId)
        );
    }

    @Operation(summary = "Get assignment detail")
    @GetMapping("/{assignmentId}")
    public ApiResponse<AssignmentDetailResponse> getAssignment(
            @PathVariable UUID assignmentId
    ) {
        return ApiResponse.success(
                assignmentService.getAssignmentById(assignmentId)
        );
    }

    @Operation(summary = "Update assignment")
    @PutMapping("/{assignmentId}")
    public ApiResponse<AssignmentResponse> updateAssignment(
            @PathVariable UUID assignmentId,
            @RequestBody UpdateAssignmentRequest request
    ) {
        return ApiResponse.success(
                assignmentService.updateAssignment(assignmentId, request)
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
                assignmentService.addLibraryProblemToAssignment(
                        topicId,
                        assignmentId,
                        request.getProblemId()
                )
        );
    }

    @Operation(summary = "Soft delete assignment")
    @DeleteMapping("/{assignmentId}")
    public ApiResponse<?> deleteAssignment(@PathVariable UUID assignmentId) {
        assignmentService.deleteAssignment(assignmentId);
        return ApiResponse.success(null);
    }
}
