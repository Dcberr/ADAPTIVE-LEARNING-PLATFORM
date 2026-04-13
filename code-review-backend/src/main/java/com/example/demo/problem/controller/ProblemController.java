package com.example.demo.problem.controller;

import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;
import com.example.demo.problem.service.ProblemService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Problem", description = "APIs for problem management")
@RestController
@RequestMapping("/problems")
@RequiredArgsConstructor
public class ProblemController {

    private final ProblemService problemService;

    @Operation(summary = "Create a new problem")
    @PostMapping
    public ApiResponse<ProblemResponse> createProblem(
            @RequestBody CreateProblemRequest request
    ) {
        return ApiResponse.success(
                problemService.createProblem(request)
        );
    }

    @Operation(summary = "Get problem detail")
    @GetMapping("/{problemId}")
    public ApiResponse<ProblemResponse> getProblem(
            @Parameter(description = "Problem ID")
            @PathVariable UUID problemId
    ) {
        return ApiResponse.success(
                problemService.getProblem(problemId)
        );
    }

    @Operation(summary = "Get problem by assignment ID")
        @GetMapping("/assignment/{assignmentId}")       
        public ApiResponse<ProblemResponse> getProblemByAssignmentId(
                @Parameter(description = "Assignment ID")
                @PathVariable UUID assignmentId
        ) {
        return ApiResponse.success(
                problemService.getProblemByAssignmentId(assignmentId)
        );
        }

    @Operation(summary = "Update problem starter code templates")
    @PutMapping("/templates")
    public ApiResponse<ProblemResponse> updateProblemTemplate(
            @RequestBody UpdateProblemTemplateRequest request
    ) {
        return ApiResponse.success(
                problemService.updateProblemTemplate(request)
        );
    }
}