package com.example.demo.submission.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.submission.dto.*;
import com.example.demo.submission.entity.Submission;

public interface SubmissionService {

    SubmissionResponse submit(UUID userId, SubmitCodeRequest request);

    // List<SubmissionHistoryResponse> getUserSubmissions(UUID userId);

    public List<SubmissionOverviewResponse> getUserSubmissionOverview(UUID userId);

    public SubmissionDetailResponse getSubmissionDetail(UUID submissionId); 

    public List<SubmissionOverviewResponse> getProblemSubmissions(UUID problemId);

    public List<SubmissionResponse> getUserSubmissionsByAssignmentId(UUID userId, UUID assignmentId);

    public List<SubmissionResponse> getAllSubmissionsByAssignmentId(UUID assignmentId);

    public List<Submission> getAllSubmissionsByProblemIdAndUserId(UUID userId, UUID problemId);

}