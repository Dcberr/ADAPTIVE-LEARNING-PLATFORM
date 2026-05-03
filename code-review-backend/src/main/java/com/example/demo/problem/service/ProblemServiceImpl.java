package com.example.demo.problem.service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
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
import com.example.demo.problem.dto.ProblemOverviewResponse;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.dto.SearchLibraryProblemRequest;
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
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Subquery;

@Service
@RequiredArgsConstructor
public class ProblemServiceImpl implements ProblemService {

    private static final Pattern FILTER_PATTERN = Pattern.compile(
            "(?i)(source|title|difficulty|externalId|external_id|tag|tags):(\"[^\"]*\"|'[^']*'|\\S+)"
    );
    private static final Pattern TOKEN_PATTERN = Pattern.compile("\"([^\"]*)\"|'([^']*)'|(\\S+)");

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
    public PageResponse<ProblemOverviewResponse> getAllLibraryProblems(int page, int size) {
        Page<Problem> problemPage = problemRepository.findAllByTypeOrderByCreatedAtDesc(
                ProblemType.LIBRARY,
                PageRequest.of(page, size)
        );

        List<ProblemOverviewResponse> content = problemPage.getContent().stream()
                .map(this::mapOverview)
                .toList();

        return PageResponse.<ProblemOverviewResponse>builder()
                .content(content)
                .page(problemPage.getNumber())
                .size(problemPage.getSize())
                .totalElements(problemPage.getTotalElements())
                .totalPages(problemPage.getTotalPages())
                .build();
    }

    @Override
    public PageResponse<ProblemOverviewResponse> searchLibraryProblems(SearchLibraryProblemRequest request, int page, int size) {
        Page<Problem> problemPage = problemRepository.findAll(
                buildLibrarySearchSpecification(request),
                PageRequest.of(page, size)
        );

        List<ProblemOverviewResponse> content = problemPage.getContent().stream()
                .map(this::mapOverview)
                .toList();

        return PageResponse.<ProblemOverviewResponse>builder()
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

    private ProblemOverviewResponse mapOverview(Problem problem) {
        return ProblemOverviewResponse.builder()
                .id(problem.getId())
                .externalId(problem.getExternalId())
                .title(problem.getTitle())
                .difficulty(problem.getDifficulty())
                .tags(getProblemTags(problem.getId()))
                .build();
    }

    private Specification<Problem> buildLibrarySearchSpecification(SearchLibraryProblemRequest request) {
        LibrarySearchCriteria criteria = parseSearchCriteria(request.getQ());

        return (root, query, cb) -> {
            query.distinct(true);

            List<Predicate> predicates = new ArrayList<>();
            predicates.add(cb.equal(root.get("type"), ProblemType.LIBRARY));

            if (criteria.source() != null && !criteria.source().isBlank()) {
                predicates.add(cb.equal(cb.lower(root.get("source")), criteria.source()));
            }

            if (criteria.title() != null && !criteria.title().isBlank()) {
                predicates.add(cb.like(
                        cb.lower(root.get("title")),
                        "%" + criteria.title() + "%"
                ));
            }

            if (criteria.difficulty() != null && !criteria.difficulty().isBlank()) {
                predicates.add(cb.equal(
                        cb.lower(root.get("difficulty")),
                        criteria.difficulty()
                ));
            }

            if (criteria.externalId() != null && !criteria.externalId().isBlank()) {
                predicates.add(cb.like(
                        cb.lower(root.get("externalId")),
                        "%" + criteria.externalId() + "%"
                ));
            }

            for (String tag : criteria.tags()) {
                Subquery<UUID> subquery = query.subquery(UUID.class);
                var tagRoot = subquery.from(ProblemTag.class);
                subquery.select(tagRoot.get("problemId"))
                        .where(
                                cb.equal(tagRoot.get("problemId"), root.get("id")),
                                cb.equal(cb.lower(tagRoot.get("tag")), tag)
                        );
                predicates.add(cb.exists(subquery));
            }

            for (String keyword : criteria.keywords()) {
                List<Predicate> keywordPredicates = new ArrayList<>();
                String pattern = "%" + keyword + "%";

                keywordPredicates.add(cb.like(cb.lower(root.get("source")), pattern));
                keywordPredicates.add(cb.like(cb.lower(root.get("title")), pattern));
                keywordPredicates.add(cb.like(cb.lower(root.get("difficulty")), pattern));
                keywordPredicates.add(cb.like(cb.lower(root.get("externalId")), pattern));

                Subquery<UUID> tagSubquery = query.subquery(UUID.class);
                var tagRoot = tagSubquery.from(ProblemTag.class);
                tagSubquery.select(tagRoot.get("problemId"))
                        .where(
                                cb.equal(tagRoot.get("problemId"), root.get("id")),
                                cb.like(cb.lower(tagRoot.get("tag")), pattern)
                        );
                keywordPredicates.add(cb.exists(tagSubquery));

                predicates.add(cb.or(keywordPredicates.toArray(new Predicate[0])));
            }

            query.orderBy(cb.desc(root.get("createdAt")));
            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }

    private LibrarySearchCriteria parseSearchCriteria(String rawQuery) {
        if (rawQuery == null || rawQuery.isBlank()) {
            return new LibrarySearchCriteria(null, null, null, null, List.of(), List.of());
        }

        StringBuilder freeText = new StringBuilder();
        String query = rawQuery.trim();
        Matcher matcher = FILTER_PATTERN.matcher(query);
        int lastEnd = 0;

        String source = null;
        String title = null;
        String difficulty = null;
        String externalId = null;
        Set<String> tags = new LinkedHashSet<>();

        while (matcher.find()) {
            freeText.append(query, lastEnd, matcher.start()).append(' ');

            String key = matcher.group(1).toLowerCase();
            String value = normalizeSearchValue(matcher.group(2));
            if (value.isBlank()) {
                lastEnd = matcher.end();
                continue;
            }

            switch (key) {
                case "source" -> source = value;
                case "title" -> title = value;
                case "difficulty" -> difficulty = value;
                case "externalid", "external_id" -> externalId = value;
                case "tag", "tags" -> {
                    for (String tag : value.split(",")) {
                        String normalizedTag = tag.trim().toLowerCase();
                        if (!normalizedTag.isBlank()) {
                            tags.add(normalizedTag);
                        }
                    }
                }
            }

            lastEnd = matcher.end();
        }

        freeText.append(query.substring(lastEnd));

        List<String> keywords = extractKeywords(freeText.toString());

        return new LibrarySearchCriteria(
                source,
                title,
                difficulty,
                externalId,
                List.copyOf(tags),
                keywords
        );
    }

    private List<String> extractKeywords(String input) {
        List<String> keywords = new ArrayList<>();
        Matcher matcher = TOKEN_PATTERN.matcher(input);

        while (matcher.find()) {
            String value = matcher.group(1) != null ? matcher.group(1)
                    : matcher.group(2) != null ? matcher.group(2)
                    : matcher.group(3);
            String normalizedValue = normalizeSearchValue(value);
            if (!normalizedValue.isBlank()) {
                keywords.add(normalizedValue);
            }
        }

        return keywords;
    }

    private String normalizeSearchValue(String value) {
        if (value == null) {
            return "";
        }

        String normalized = value.trim();
        if ((normalized.startsWith("\"") && normalized.endsWith("\""))
                || (normalized.startsWith("'") && normalized.endsWith("'"))) {
            normalized = normalized.substring(1, normalized.length() - 1);
        }

        return normalized.trim().toLowerCase();
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

        if (request.isSaveToLibrary()) {
            Problem libraryProblem = Problem.builder()
                    .title(request.getTitle())
                    .description(request.getDescription())
                    .difficulty(request.getDifficulty())
                    .problemConstraint(request.getProblemConstraint())
                    .starterCodes(normalizeStarterCodes(request.getStarterCodes()))
                    .type(ProblemType.LIBRARY)
                    .source("SYSTEM")
                    .createdAt(Instant.now())
                    .build();

            problemRepository.save(libraryProblem);

            saveTestcases(libraryProblem.getId(), request.getTestcases());
            replaceProblemTags(libraryProblem.getId(), getProblemTags(problem.getId()));
        }

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

    private record LibrarySearchCriteria(
            String source,
            String title,
            String difficulty,
            String externalId,
            List<String> tags,
            List<String> keywords
    ) {
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
