package com.example.demo.problem.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.common.response.PageResponse;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.LeetCodeImportRequest;
import com.example.demo.problem.dto.LeetCodeProblemPageResponse;
import com.example.demo.problem.dto.ProblemLibraryRequest;
import com.example.demo.problem.dto.ProblemOverviewResponse;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.UpdateProblemSourceRequest;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;

public interface ProblemService {

    ProblemResponse createProblem(CreateProblemRequest request);

    ProblemResponse getProblem(UUID problemId);

    ProblemResponse getProblemByAssignmentId(UUID assignmentId);

    PageResponse<ProblemOverviewResponse> getAllLibraryProblems(int page, int size);

    LeetCodeProblemPageResponse getLeetCodeProblems(int page, int limit);

    /**
     * Update problem starter code templates
     */
    ProblemResponse updateProblemTemplate(UpdateProblemTemplateRequest request);

    public ProblemResponse createManualProblem(CreateProblemRequest request);

    public ProblemResponse createManualLibraryProblem(ProblemLibraryRequest request);

    public List<ProblemResponse> batchInsertLeetCode(List<LeetCodeImportRequest> requests);

    public List<ProblemResponse> batchUpdateLeetCode(List<LeetCodeImportRequest> requests);

    public ProblemResponse updateProblemSourceToLibrary(UpdateProblemSourceRequest request);

}
