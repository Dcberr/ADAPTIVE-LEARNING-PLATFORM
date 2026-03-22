package com.example.demo.problem.service;

import java.time.Instant;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;    

    @Override
    public ProblemResponse createProblem(CreateProblemRequest request) {

        Problem problem = Problem.builder()
                // .title(request.getTitle())
                .description(request.getDescription())
                // .difficulty(request.getDifficulty())
                // .source(request.getSource())
                .createdAt(Instant.now())
                .build();

        problemRepository.save(problem);

        if (request.getTestcases() != null) {
            for (CreateProblemRequest.TestcaseRequest t : request.getTestcases()) {

                testcaseRepository.save(
                        Testcase.builder()
                                .problemId(problem.getId())
                                .input(t.getInput())
                                .expectedOutput(t.getExpectedOutput())
                                .isSample(t.isSample())
                                .build()
                );
            }
        }

        return map(problem);
    }

    @Override
    public ProblemResponse getProblem(UUID problemId) {

        Problem problem = problemRepository.findById(problemId)
                .orElseThrow();

        return map(problem);
    }

    private ProblemResponse map(Problem problem) {

        return ProblemResponse.builder()
                .id(problem.getId())
                .title(problem.getTitle())
                .description(problem.getDescription())
                .difficulty(problem.getDifficulty())
                .source(problem.getSource())
                .build();
    }
}