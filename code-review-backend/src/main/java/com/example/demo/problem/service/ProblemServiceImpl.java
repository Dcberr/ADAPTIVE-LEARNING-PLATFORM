package com.example.demo.problem.service;

import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.problem.client.LeetCodeClient;
import com.example.demo.problem.dto.CreateProblemRequest;
// import com.example.demo.problem.dto.CreateProblemRequest.TestcaseRequest;
import com.example.demo.problem.dto.LeetCodeImportRequest;
import com.example.demo.problem.dto.LeetCodeProblemPageResponse;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.TestcaseDto;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.utils.CodeExtractor;
import com.example.demo.problem.utils.LeetCodeStarterCodeGenerator;

import jakarta.transaction.Transactional;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;    
    private final AssignmentProblemRepository assignmentProblemRepository;
    private final LeetCodeClient leetCodeClient;
    private final LeetCodeStarterCodeGenerator leetCodeStarterCodeGenerator;
    private final TestcaseService testcaseService;

    @Override
    public ProblemResponse createProblem(CreateProblemRequest request) {
        // Map<String, String> starterCodes = resolveStarterCodes(request);

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
            for (TestcaseDto t : request.getTestcases()) {

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

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(problem.getId());

        return map(problem, testcases);
    }

    // private Map<String, String> resolveStarterCodes(CreateProblemRequest request) {
    //     if (request.getStarterCodes() != null && !request.getStarterCodes().isEmpty()) {
    //         return request.getStarterCodes();
    //     }

    //     if (request.getLeetCodeCodeSnippet() == null || request.getLeetCodeCodeSnippet().isBlank()) {
    //         return Collections.emptyMap();
    //     }

    //     return leetCodeStarterCodeGenerator.generateStarterCodes(
    //             request.getLeetCodeLanguage(),
    //             request.getLeetCodeCodeSnippet()
    //     );
    // }

    // @Override
    // public ProblemResponse getProblem(UUID problemId) {

    //     Problem problem = problemRepository.findById(problemId)
    //             .orElseThrow();

    //     return map(problem);
    // }

    public ProblemResponse getProblem(UUID id) {

        Problem problem = problemRepository.findById(id)
                .orElseThrow();

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(id);

        return map(problem, testcases);
    }
    @Override
    public ProblemResponse getProblemByAssignmentId(UUID assignmentId) {

        AssignmentProblem problem = assignmentProblemRepository.findByAssignmentId(assignmentId);

        List<TestcaseResponse> testcases =
        testcaseService.getTestcasesByProblem(problem.getId());

        return map(problemRepository.findById(problem.getProblemId())
                .orElseThrow(), testcases);
    }

    @Override
    public LeetCodeProblemPageResponse getLeetCodeProblems(int page, int limit) {
        return leetCodeClient.getProblems(page, limit);
    }

    @Override
    public ProblemResponse updateProblemTemplate(UpdateProblemTemplateRequest request) {
        
        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new RuntimeException("Problem not found"));

        problem.setStarterCodes(request.getStarterCodes());
        
        problemRepository.save(problem);

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(problem.getId());

        return map(problem, testcases);
    }

    private ProblemResponse map(Problem problem, List<TestcaseResponse> testcases) {

        Map<String, String> functionSkeletons = new HashMap<>();

        if (problem.getStarterCodes() != null) {
            problem.getStarterCodes().forEach((lang, template) -> {
                functionSkeletons.put(lang, CodeExtractor.extractFunctionSkeleton(template));
            });
        }

        return ProblemResponse.builder()
                .id(problem.getId())
                .title(problem.getTitle())
                .description(problem.getDescription())
                .difficulty(problem.getDifficulty())
                .problemConstraint(problem.getProblemConstraint())
                .type(problem.getType())
                .functionSkeletons(functionSkeletons)
                .testcases(testcases)
                .build();
    }

    @Override
    public ProblemResponse createManualProblem(CreateProblemRequest request) {

        Problem problem = Problem.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .difficulty(request.getDifficulty())
                .problemConstraint(request.getProblemConstraint())
                .starterCodes(request.getStarterCodes())
                .type(ProblemType.MANUAL)
                .source("SYSTEM")
                .createdAt(Instant.now())
                .build();

        problemRepository.save(problem);

        saveTestcases(problem.getId(), request.getTestcases());

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(problem.getId());

        return map(problem, testcases);

        
    }

    @Transactional
    @Override
    public void batchInsertLeetCode(List<LeetCodeImportRequest> requests) {

        for (LeetCodeImportRequest req : requests) {

            boolean exists = problemRepository.existsBySourceAndExternalId(
                    "LEETCODE", req.getExternalId()
            );

            if (exists) continue;

            Problem problem = Problem.builder()
                    .title(req.getTitle())
                    .description(req.getDescription())
                    .difficulty(req.getDifficulty())
                    .problemConstraint(req.getConstraints())
                    .starterCodes(req.getStarterCodes())
                    .type(ProblemType.LEETCODE)
                    .source("LEETCODE")
                    .externalId(req.getExternalId())
                    .createdAt(Instant.now())
                    .build();

            problemRepository.save(problem);

            saveTestcases(problem.getId(), req.getTestcases());
        }
    }

    private void saveTestcases(UUID problemId, List<TestcaseDto> testcases) {

        if (testcases == null) return;

        for (TestcaseDto t : testcases) {
            testcaseRepository.save(
                    Testcase.builder()
                            .problemId(problemId)
                            .input(t.getInput())
                            .expectedOutput(t.getExpectedOutput())
                            .isHidden(t.isHidden())
                            .explanation(t.getExplanation())
                            .build()
            );
        }
    }
    
}
