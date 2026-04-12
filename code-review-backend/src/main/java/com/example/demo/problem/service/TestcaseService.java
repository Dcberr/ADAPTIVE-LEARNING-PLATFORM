package com.example.demo.problem.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.problem.dto.CreateTestcaseRequest;
import com.example.demo.problem.dto.TestcaseResponse;

public interface TestcaseService {

    TestcaseResponse createTestcase(CreateTestcaseRequest request);

    List<TestcaseResponse> getTestcasesByProblem(UUID problemId);

    List<TestcaseResponse> getTestcasesByAssignment(UUID assignmentId);

}