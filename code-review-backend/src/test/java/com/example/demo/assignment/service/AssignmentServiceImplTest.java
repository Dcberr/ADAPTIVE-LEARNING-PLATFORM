package com.example.demo.assignment.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.entity.AssignmentProblem;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.assignment.mapper.AssignmentMapper;
import com.example.demo.assignment.repository.AssignmentProblemRepository;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.entity.ProblemType;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.problem.service.ProblemService;
import com.example.demo.topic.repository.TopicRepository;

class AssignmentServiceImplTest {

    private final AssignmentRepository assignmentRepository = org.mockito.Mockito.mock(AssignmentRepository.class);
    private final AssignmentProblemRepository assignmentProblemRepository = org.mockito.Mockito
            .mock(AssignmentProblemRepository.class);
    private final ProblemRepository problemRepository = org.mockito.Mockito.mock(ProblemRepository.class);
    private final TestcaseRepository testcaseRepository = org.mockito.Mockito.mock(TestcaseRepository.class);
    private final ProblemService problemService = org.mockito.Mockito.mock(ProblemService.class);
    private final AssignmentMapper assignmentMapper = org.mockito.Mockito.mock(AssignmentMapper.class);
    private final TopicRepository topicRepository = org.mockito.Mockito.mock(TopicRepository.class);

    private final AssignmentServiceImpl assignmentService = new AssignmentServiceImpl(
            assignmentRepository,
            assignmentProblemRepository,
            problemRepository,
            testcaseRepository,
            problemService,
            assignmentMapper,
            topicRepository);

    @Test
    @DisplayName("Should clone library problem into assignment class problem before linking")
    void shouldCloneLibraryProblemIntoAssignmentClassProblemBeforeLinking() {
        UUID topicId = UUID.randomUUID();
        UUID assignmentId = UUID.randomUUID();
        UUID libraryProblemId = UUID.randomUUID();
        UUID clonedProblemId = UUID.randomUUID();

        Assignment assignment = Assignment.builder()
                .id(assignmentId)
                .topicId(topicId)
                .title("Week 1")
                .status(AssignmentStatus.PENDING)
                .createdAt(Instant.now())
                .build();

        Map<String, String> starterCodes = Map.of(
                "cpp",
                "class Solution { public: vector<string> addOperators(string num, int target) { } };");

        Problem libraryProblem = Problem.builder()
                .id(libraryProblemId)
                .title("Expression Add Operators")
                .description("desc")
                .difficulty("HARD")
                .problemConstraint("constraints")
                .starterCodes(starterCodes)
                .type(ProblemType.LIBRARY)
                .source("LEETCODE")
                .build();

        List<Testcase> testcases = List.of(
                Testcase.builder()
                        .problemId(libraryProblemId)
                        .input("\"123\"\n6")
                        .expectedOutput("[\"1+2+3\",\"1*2*3\"]")
                        .isHidden(false)
                        .explanation("sample")
                        .build());

        ProblemResponse clonedProblem = ProblemResponse.builder()
                .id(clonedProblemId)
                .build();

        when(assignmentRepository.findByIdAndDeletedAtIsNull(assignmentId)).thenReturn(Optional.of(assignment));
        when(problemRepository.findById(libraryProblemId)).thenReturn(Optional.of(libraryProblem));
        when(testcaseRepository.findByProblemId(libraryProblemId)).thenReturn(testcases);
        when(problemService.createManualProblem(any(CreateProblemRequest.class))).thenReturn(clonedProblem);
        when(assignmentProblemRepository.existsByAssignmentIdAndProblemId(assignmentId, clonedProblemId))
                .thenReturn(false);

        assignmentService.addLibraryProblemToAssignment(topicId, assignmentId, libraryProblemId);

        ArgumentCaptor<CreateProblemRequest> createProblemCaptor = ArgumentCaptor.forClass(CreateProblemRequest.class);
        verify(problemService).createManualProblem(createProblemCaptor.capture());

        CreateProblemRequest request = createProblemCaptor.getValue();
        assertEquals(libraryProblem.getTitle(), request.getTitle());
        assertEquals(libraryProblem.getDescription(), request.getDescription());
        assertEquals(libraryProblem.getDifficulty(), request.getDifficulty());
        assertEquals(libraryProblem.getProblemConstraint(), request.getProblemConstraint());
        assertEquals(starterCodes, request.getStarterCodes());
        assertEquals(assignmentId, request.getAssignmentId());
        assertEquals(1, request.getTestcases().size());
        assertEquals(testcases.getFirst().getInput(), request.getTestcases().getFirst().getInput());
        assertEquals(testcases.getFirst().getExpectedOutput(), request.getTestcases().getFirst().getExpectedOutput());

        ArgumentCaptor<AssignmentProblem> mappingCaptor = ArgumentCaptor.forClass(AssignmentProblem.class);
        verify(assignmentProblemRepository).save(mappingCaptor.capture());
        assertEquals(assignmentId, mappingCaptor.getValue().getAssignmentId());
        assertEquals(clonedProblemId, mappingCaptor.getValue().getProblemId());

        verify(assignmentProblemRepository, never()).existsByAssignmentIdAndProblemId(assignmentId, libraryProblemId);
    }
}
