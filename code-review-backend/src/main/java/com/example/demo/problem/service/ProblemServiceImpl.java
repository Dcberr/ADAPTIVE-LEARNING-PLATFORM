package com.example.demo.problem.service;

import java.time.Instant;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.service.AssignmentServiceImpl;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.repository.ProblemRepository;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private final ProblemRepository problemRepository;
    private final AssignmentServiceImpl assignmentService;

    @Override
    public ProblemResponse createProblem(CreateProblemRequest request) {

        Problem problem = Problem.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .difficulty(request.getDifficulty())
                .source(request.getSource())
                .createdAt(Instant.now())
                .build();

        problemRepository.save(problem);

        if (request.getAssignmentId() != null) {
            assignmentService.addProblemToAssignment(request.getAssignmentId(), problem.getId());
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