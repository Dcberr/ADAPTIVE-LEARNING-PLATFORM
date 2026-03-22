package com.example.demo.submission.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;

import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.service.ExecutionService;
import com.example.demo.problem.dto.TestcaseResponse;
import com.example.demo.problem.entity.Problem;
import com.example.demo.problem.repository.ProblemRepository;
import com.example.demo.problem.repository.TestcaseRepository;
import com.example.demo.submission.dto.*;
import com.example.demo.submission.entity.Submission;
import com.example.demo.submission.repository.SubmissionRepository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubmissionServiceImpl implements SubmissionService {

    private final SubmissionRepository submissionRepository;
    private final ExecutionService executionService;
    private final ProblemRepository problemRepository;
    private final TestcaseRepository testcaseRepository;

    @Override
    public SubmissionResponse submit(
            UUID userId,
            SubmitCodeRequest request
    ) {

        RunTestcaseRequest judgeRequest = new RunTestcaseRequest();

        judgeRequest.setProblemId(request.getProblemId());
        judgeRequest.setLanguage(request.getLanguage());
        judgeRequest.setCode(request.getCode());

        RunCodeResponse result =
                executionService.runByTestcase(judgeRequest);

        Submission submission =
                Submission.builder()
                        .userId(userId)
                        .problemId(request.getProblemId())
                        .language(request.getLanguage())
                        .code(request.getCode())
                        .status(result.getStatus().name())
                        // .runtime(result.getRuntime())
                        .passedTestcases(result.getPassedTestcases())
                        .totalTestcases(result.getTotalTestcases())
                        .score(String.valueOf((double) result.getPassedTestcases() / result.getTotalTestcases() * 100))
                        .createdAt(Instant.now())
                        .build();

        submissionRepository.save(submission);

        return SubmissionResponse.builder()
                .id(submission.getId())
                .status(submission.getStatus())
                .runtime(submission.getRuntime())
                .passedTestcases(submission.getPassedTestcases())
                .totalTestcases(submission.getTotalTestcases())
                .build();
    }

    @Override
    public List<SubmissionHistoryResponse> getUserSubmissions(UUID userId) {

        return submissionRepository.findByUserId(userId)
                .stream()
                .map(s -> SubmissionHistoryResponse.builder()
                        .id(s.getId())
                        .problemId(s.getProblemId())
                        .status(s.getStatus())
                        .language(s.getLanguage())
                        .code(s.getCode())
                        .createdAt(s.getCreatedAt())
                        .score(String.valueOf((double) s.getPassedTestcases() / s.getTotalTestcases() * 100))
                        .build())
                .toList();
    }

    @Override
    public List<SubmissionOverviewResponse> getUserSubmissionOverview(UUID userId) {
        log.info(submissionRepository.getSubmissionOverview(userId).toString());
        SubmissionOverviewResponse response = submissionRepository.getSubmissionOverview(userId).get(0);
        return submissionRepository.getSubmissionOverview(userId);
    }

    @Override
    public SubmissionDetailResponse getSubmissionDetail(UUID submissionId) {

        Submission submission =
                submissionRepository.findById(submissionId)
                        .orElseThrow();

        Problem problem =
                problemRepository.findById(submission.getProblemId())
                        .orElseThrow();

        List<TestcaseResponse> testcases =
                testcaseRepository.findByProblemId(problem.getId())
                        .stream()
                        .map(tc -> TestcaseResponse.builder()
                                .id(tc.getId())
                                .input(tc.getInput())
                                .problemId(problem.getId())
                                .expectedOutput(tc.getExpectedOutput())
                                .isSample(tc.isSample())
                                .build())
                        .toList();

        return SubmissionDetailResponse.builder()
                .submissionId(submission.getId())
                .problemTitle(problem.getTitle())
                .score(String.valueOf((double) submission.getPassedTestcases() / submission.getTotalTestcases() * 100))
                .problemDescription(problem.getDescription())
                .difficulty(problem.getDifficulty())
                .code(submission.getCode())
                .language(submission.getLanguage())
                .status(submission.getStatus())
                .testcases(testcases)
                .build();
        }

        @Override
        public List<SubmissionOverviewResponse> getProblemSubmissions(UUID problemId) {

            return submissionRepository.getSubmissionOverviewByProblem(problemId);      
        }
}