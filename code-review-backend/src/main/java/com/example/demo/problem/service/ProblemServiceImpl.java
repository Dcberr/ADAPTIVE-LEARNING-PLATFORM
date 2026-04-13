package com.example.demo.problem.service;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.utils.CodeExtractor;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;    
    private final AssignmentProblemRepository assignmentProblemRepository;

    @Override
    public ProblemResponse createProblem(CreateProblemRequest request) {

        Problem problem = Problem.builder()
                // .title(request.getTitle())
                .description(request.getDescription())
                .problemConstraint(request.getProblemConstraint())
                .starterCodes(request.getStarterCodes())
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
                                .isHidden(t.isHidden())
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

    @Override
    public ProblemResponse getProblemByAssignmentId(UUID assignmentId) {

        AssignmentProblem problem = assignmentProblemRepository.findByAssignmentId(assignmentId);

        return map(problemRepository.findById(problem.getProblemId())
                .orElseThrow());
    }

    @Override
    public ProblemResponse updateProblemTemplate(UpdateProblemTemplateRequest request) {
        
        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new RuntimeException("Problem not found"));

        problem.setStarterCodes(request.getStarterCodes());
        
        problemRepository.save(problem);

        return map(problem);
    }

    private ProblemResponse map(Problem problem) {
        
        Map<String, String> functionSkeletons = new HashMap<>();
        
        // Extract function skeleton from templates if available
        if (problem.getStarterCodes() != null && !problem.getStarterCodes().isEmpty()) {
            problem.getStarterCodes().forEach((language, template) -> {
                functionSkeletons.put(language, CodeExtractor.extractFunctionSkeleton(template));
            });
        }

        return ProblemResponse.builder()
                .id(problem.getId())
                // .title(problem.getTitle())
                .description(problem.getDescription())
                .problemConstraint(problem.getProblemConstraint())
                .functionSkeletons(functionSkeletons)
                // .difficulty(problem.getDifficulty())
                // .source(problem.getSource())
                .build();
    }
}