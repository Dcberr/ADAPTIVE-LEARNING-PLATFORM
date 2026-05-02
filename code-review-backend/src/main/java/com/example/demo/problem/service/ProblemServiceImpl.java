package com.example.demo.problem.service;

import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.common.response.PageResponse;
import com.example.demo.problem.client.LeetCodeClient;
import com.example.demo.problem.dto.CreateProblemRequest;
// import com.example.demo.problem.dto.CreateProblemRequest.TestcaseRequest;
import com.example.demo.problem.dto.LeetCodeImportRequest;
import com.example.demo.problem.dto.LeetCodeProblemPageResponse;
import com.example.demo.problem.dto.ProblemLibraryRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.TestcaseDto;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.dto.UpdateProblemSourceRequest;
import com.example.demo.problem.dto.UpdateProblemTemplateRequest;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemTag;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.ProblemTagRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.utils.CodeExtractor;
import com.example.demo.problem.utils.LeetCodeStarterCodeGenerator;

import jakarta.transaction.Transactional;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private final ProblemRepository problemRepository;
    private final ProblemTagRepository problemTagRepository;
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
                .starterCodes(normalizeStarterCodes(request.getStarterCodes()))
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
    public PageResponse<ProblemResponse> getAllLeetCodeProblems(int page, int size) {
        Page<Problem> problemPage = problemRepository.findAllBySourceOrderByCreatedAtDesc(
                "LEETCODE",
                PageRequest.of(page, size)
        );

        List<ProblemResponse> content = problemPage.getContent().stream()
                .map(problem -> map(
                    problem,
                    testcaseService.getTestcasesByProblem(problem.getId())
                ))
                .toList();

        return PageResponse.<ProblemResponse>builder()
                .content(content)
                .page(problemPage.getNumber())
                .size(problemPage.getSize())
                .totalElements(problemPage.getTotalElements())
                .totalPages(problemPage.getTotalPages())
                .build();
    }

    @Override
    public LeetCodeProblemPageResponse getLeetCodeProblems(int page, int limit) {
        return leetCodeClient.getProblems(page, limit);
    }

    @Override
    public ProblemResponse updateProblemTemplate(UpdateProblemTemplateRequest request) {
        
        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new RuntimeException("Problem not found"));

        problem.setStarterCodes(normalizeStarterCodes(request.getStarterCodes()));
        
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

        List<String> similarIds = Optional.ofNullable(problem.getSimilarProblems())
            .orElse(Collections.emptySet())
            .stream()
            .map(Problem::getExternalId)
            .toList();

        return ProblemResponse.builder()
                .id(problem.getId())
                .title(problem.getTitle())
                .description(problem.getDescription())
                .difficulty(problem.getDifficulty())
                .problemConstraint(problem.getProblemConstraint())
                .externalId(problem.getExternalId())
                .type(problem.getType())
                .functionSkeletons(functionSkeletons)
                .similarQuestionIds(similarIds)
                .tags(getProblemTags(problem.getId()))
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
                .starterCodes(normalizeStarterCodes(request.getStarterCodes()))
                .type(ProblemType.CLASS)
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
    public ProblemResponse createManualLibraryProblem(ProblemLibraryRequest request) {

        // validateLeetCodeExternalId(request.getExternalId(), null);

        Problem problem = Problem.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .difficulty(request.getDifficulty())
                .problemConstraint(request.getConstraints())
                .starterCodes(normalizeStarterCodes(request.getStarterCodes()))
                .type(ProblemType.LIBRARY)
                .source("SYSTEM")
                // .externalId(request.getExternalId())
                .createdAt(Instant.now())
                .build();

        problemRepository.save(problem);

        saveTestcases(problem.getId(), request.getTestcases());
        replaceProblemTags(problem.getId(), request.getTags());
        // syncSimilarProblems(problem, request.getSimilarQuestionIds());
        problemRepository.save(problem);

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(problem.getId());

        return map(problem, testcases);
    }

    @Transactional
    @Override
    public List<ProblemResponse> batchInsertLeetCode(List<LeetCodeImportRequest> requests) {

        Map<String, Problem> cache = new HashMap<>();

        // =========================
        // PHASE 1: INSERT / GET
        // =========================
        for (LeetCodeImportRequest req : requests) {

            Problem problem = problemRepository
                    .findBySourceAndExternalId("LEETCODE", req.getExternalId())
                    .orElseGet(() -> {

                        Problem newProblem = Problem.builder()
                                .title(req.getTitle())
                                .description(req.getDescription())
                                .difficulty(req.getDifficulty())
                                .problemConstraint(req.getConstraints())
                                .starterCodes(normalizeStarterCodes(req.getStarterCodes()))
                                .type(ProblemType.LIBRARY)
                                .source("LEETCODE")
                                .externalId(req.getExternalId())
                                .createdAt(Instant.now())
                                .build();

                        problemRepository.save(newProblem);

                        saveTestcases(newProblem.getId(), req.getTestcases());
                        replaceProblemTags(newProblem.getId(), req.getTags());

                        return newProblem;
                    });

            replaceProblemTags(problem.getId(), req.getTags());

            cache.put(req.getExternalId(), problem);
        }

        // =========================
        // PHASE 2: LINK SIMILAR
        // =========================
        for (LeetCodeImportRequest req : requests) {

            Problem current = cache.get(req.getExternalId());
            syncSimilarProblems(current, req.getSimilarQuestionIds());
        }

        // =========================
        // SAVE ALL (flush)
        // =========================
        problemRepository.saveAll(cache.values());

        // =========================
        // BUILD RESPONSE
        // =========================
        return cache.values().stream()
                .map(problem -> {
                    List<TestcaseResponse> testcases =
                            testcaseService.getTestcasesByProblem(problem.getId());

                    return map(problem, testcases);
                })
                .toList();
    }

    @Transactional
    @Override
    public List<ProblemResponse> batchUpdateLeetCode(List<LeetCodeImportRequest> requests) {

        Map<String, Problem> cache = new HashMap<>();

        for (LeetCodeImportRequest req : requests) {
            Problem problem = problemRepository
                    .findBySourceAndExternalId("LEETCODE", req.getExternalId())
                    .orElseGet(() -> Problem.builder()
                            .type(ProblemType.LIBRARY)
                            .source("LEETCODE")
                            .externalId(req.getExternalId())
                            .createdAt(Instant.now())
                            .build());

            problem.setTitle(req.getTitle());
            problem.setDescription(req.getDescription());
            problem.setDifficulty(req.getDifficulty());
            problem.setProblemConstraint(req.getConstraints());
            problem.setStarterCodes(normalizeStarterCodes(req.getStarterCodes()));
            problem.setType(ProblemType.LIBRARY);
            problem.setSource("LEETCODE");
            problem.setExternalId(req.getExternalId());
            problem.getSimilarProblems().clear();

            problemRepository.save(problem);

            testcaseRepository.deleteByProblemId(problem.getId());
            saveTestcases(problem.getId(), req.getTestcases());
            replaceProblemTags(problem.getId(), req.getTags());

            cache.put(req.getExternalId(), problem);
        }

        for (LeetCodeImportRequest req : requests) {

            Problem current = cache.get(req.getExternalId());
            syncSimilarProblems(current, req.getSimilarQuestionIds());
        }

        problemRepository.saveAll(cache.values());

        return cache.values().stream()
                .map(problem -> {
                    List<TestcaseResponse> testcases =
                            testcaseService.getTestcasesByProblem(problem.getId());

                    return map(problem, testcases);
                })
                .toList();
    }

    @Transactional
    @Override
    public ProblemResponse updateProblemSourceToLibrary(UpdateProblemSourceRequest request) {
        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new RuntimeException("Problem not found"));

        if (!"SYSTEM".equals(problem.getSource())) {
            throw new RuntimeException("Only SYSTEM problems can be converted to LEETCODE");
        }

        validateLeetCodeExternalId(request.getExternalId(), problem.getId());

        problem.setSource("LEETCODE");
        problem.setType(ProblemType.LIBRARY);
        problem.setExternalId(request.getExternalId());

        problemRepository.save(problem);

        List<TestcaseResponse> testcases =
                testcaseService.getTestcasesByProblem(problem.getId());

        return map(problem, testcases);
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

    private Map<String, String> normalizeStarterCodes(Map<String, String> starterCodes) {
        return leetCodeStarterCodeGenerator.normalizeStarterCodes(starterCodes);
    }

    private List<String> getProblemTags(UUID problemId) {
        return problemTagRepository.findByProblemId(problemId).stream()
                .map(ProblemTag::getTag)
                .toList();
    }

    private void replaceProblemTags(UUID problemId, List<String> tags) {
        problemTagRepository.deleteByProblemId(problemId);

        if (tags == null || tags.isEmpty()) {
            return;
        }

        List<ProblemTag> problemTags = tags.stream()
                .filter(tag -> tag != null && !tag.isBlank())
                .distinct()
                .map(tag -> ProblemTag.builder()
                        .problemId(problemId)
                        .tag(tag)
                        .build())
                .toList();

        problemTagRepository.saveAll(problemTags);
    }

    private void syncSimilarProblems(Problem problem, List<String> similarQuestionIds) {
        if (similarQuestionIds == null) {
            return;
        }

        for (String similarId : similarQuestionIds) {
            Problem similar = problemRepository
                    .findBySourceAndExternalId("LEETCODE", similarId)
                    .orElse(null);

            if (similar != null && !similar.getId().equals(problem.getId())) {
                problem.getSimilarProblems().add(similar);
                similar.getSimilarProblems().add(problem);
            }
        }
    }

    private void validateLeetCodeExternalId(String externalId, UUID currentProblemId) {
        if (externalId == null || externalId.isBlank()) {
            throw new RuntimeException("externalId is required for LEETCODE problem");
        }

        problemRepository.findBySourceAndExternalId("LEETCODE", externalId)
                .filter(existing -> currentProblemId == null || !existing.getId().equals(currentProblemId))
                .ifPresent(existing -> {
                    throw new RuntimeException("LeetCode problem with externalId already exists");
                });
    }
    
}
