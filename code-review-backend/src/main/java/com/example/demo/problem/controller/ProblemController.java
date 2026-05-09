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
import com.example.demo.problem.dto.SearchLibraryProblemRequest;
import com.example.demo.problem.dto.UpdateLibraryProblemRequest;
import com.example.demo.problem.dto.UpdateProblemSourceRequest;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;
import com.example.demo.problem.service.ProblemService;

import io.swagger.v3.oas.annotations.Hidden;
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
    @Hidden
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

    @Operation(summary = "Search library problems")
    @GetMapping("/library/search")
    public ApiResponse<PageResponse<ProblemOverviewResponse>> searchLibraryProblems(
            @RequestParam(required = false, name = "q") String query,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        SearchLibraryProblemRequest request = new SearchLibraryProblemRequest();
        request.setQ(query);

        return ApiResponse.success(
                problemService.searchLibraryProblems(request, page, size)
        );
    }

    @Operation(summary = "Create manual problem")
    @Hidden
    @PostMapping("/manual")
    public ApiResponse<ProblemResponse> createManualProblem(
            @RequestBody CreateProblemRequest request
    ) {
        return ApiResponse.success(
                problemService.createManualProblem(request)
        );
    }

    @Operation(summary = "Batch import LeetCode problems")
    @Hidden
    @PostMapping("/leetcode/batch")
    public ApiResponse<List<ProblemResponse>> importLeetCodeProblems(
            @RequestBody List<LeetCodeImportRequest> requests
    ) {
        return ApiResponse.success(problemService.batchInsertLeetCode(requests));
    }

    @Operation(summary = "Batch update LeetCode problems")
    @Hidden
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

    @Operation(summary = "Update library problem")
    @PutMapping("/library/{problemId}")
    public ApiResponse<ProblemResponse> updateLibraryProblem(
            @PathVariable UUID problemId,
            @RequestBody UpdateLibraryProblemRequest request
    ) {
        return ApiResponse.success(problemService.updateLibraryProblem(problemId, request));
    }

    @Operation(summary = "Soft delete library problem")
    @DeleteMapping("/library/{problemId}")
    public ApiResponse<?> deleteLibraryProblem(@PathVariable UUID problemId) {
        problemService.deleteLibraryProblem(problemId);
        return ApiResponse.success(null);
    }

    @Operation(summary = "Add problem from class to library")
    @Hidden
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
    @Hidden
    @PutMapping("/templates")
    public ApiResponse<ProblemResponse> updateProblemTemplate(
            @RequestBody UpdateProblemTemplateRequest request
    ) {
        return ApiResponse.success(
                problemService.updateProblemTemplate(request)
        );
    }
}
