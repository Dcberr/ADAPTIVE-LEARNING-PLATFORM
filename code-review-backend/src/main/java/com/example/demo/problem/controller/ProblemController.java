package com.example.demo.problem.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.common.response.PageResponse;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.LeetCodeImportRequest;
import com.example.demo.problem.dto.ProblemLibraryRequest;
import com.example.demo.problem.dto.ProblemOverviewResponse;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.UpdateProblemSourceRequest;
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
                problemService.createManualProblem(request)
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

    @Operation(summary = "Get paged library problems")
    @GetMapping("/library")
    public ApiResponse<PageResponse<ProblemOverviewResponse>> getAllLibraryProblems(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ApiResponse.success(
                problemService.getAllLibraryProblems(page, size)
        );
    }

    @Operation(summary = "Create manual problem")
    @PostMapping("/manual")
    public ApiResponse<ProblemResponse> createManualProblem(
            @RequestBody CreateProblemRequest request
    ) {
        return ApiResponse.success(
                problemService.createManualProblem(request)
        );
    }

    @Operation(summary = "Batch import LeetCode problems")
    @PostMapping("/leetcode/batch")
    public ApiResponse<List<ProblemResponse>> importLeetCodeProblems(
            @RequestBody List<LeetCodeImportRequest> requests
    ) {
        return ApiResponse.success(problemService.batchInsertLeetCode(requests));
    }

    @Operation(summary = "Batch update LeetCode problems")
    @PutMapping("/leetcode/batch")
    public ApiResponse<List<ProblemResponse>> updateLeetCodeProblems(
            @RequestBody List<LeetCodeImportRequest> requests
    ) {
        return ApiResponse.success(problemService.batchUpdateLeetCode(requests));
    }

    @Operation(summary = "Create manual Library problem")
    @PostMapping("/library/manual")
    public ApiResponse<ProblemResponse> createManualLibraryProblem(
            @RequestBody ProblemLibraryRequest request
    ) {
        return ApiResponse.success(problemService.createManualLibraryProblem(request));
    }

    @Operation(summary = "Add problem from class to library")
    @PutMapping("/source/library")
    public ApiResponse<ProblemResponse> updateProblemSourceToLibrary(
            @RequestBody UpdateProblemSourceRequest request
    ) {
        return ApiResponse.success(problemService.updateProblemSourceToLibrary(request));
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
