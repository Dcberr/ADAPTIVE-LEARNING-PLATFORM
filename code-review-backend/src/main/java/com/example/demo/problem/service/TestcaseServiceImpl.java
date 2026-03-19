package com.example.demo.problem.service;

import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.problem.dto.CreateTestcaseRequest;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.TestcaseRepository;

@Service
@RequiredArgsConstructor
public class TestcaseServiceImpl implements TestcaseService {

    private final TestcaseRepository testcaseRepository;

    @Override
    public TestcaseResponse createTestcase(CreateTestcaseRequest request) {

        Testcase testcase = Testcase.builder()
                .problemId(request.getProblemId())
                .input(request.getInput())
                .expectedOutput(request.getExpectedOutput())
                .isSample(request.isSample())
                .build();

        testcaseRepository.save(testcase);

        return map(testcase);
    }

    @Override
    public List<TestcaseResponse> getTestcasesByProblem(UUID problemId) {

        return testcaseRepository.findByProblemId(problemId)
                .stream()
                .map(this::map)
                .toList();
    }

    private TestcaseResponse map(Testcase testcase) {

        return TestcaseResponse.builder()
                .id(testcase.getId())
                .problemId(testcase.getProblemId())
                .input(testcase.getInput())
                .expectedOutput(testcase.getExpectedOutput())
                .isSample(testcase.isSample())
                .build();
    }
}