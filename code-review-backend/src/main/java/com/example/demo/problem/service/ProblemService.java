package com.example.demo.problem.service;

import java.util.UUID;

import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.LeetCodeProblemPageResponse;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;

public interface ProblemService {

    ProblemResponse createProblem(CreateProblemRequest request);

    ProblemResponse getProblem(UUID problemId);

    ProblemResponse getProblemByAssignmentId(UUID assignmentId);

    LeetCodeProblemPageResponse getLeetCodeProblems(int page, int limit);

    /**
     * Update problem starter code templates
     */
    ProblemResponse updateProblemTemplate(UpdateProblemTemplateRequest request);

}
