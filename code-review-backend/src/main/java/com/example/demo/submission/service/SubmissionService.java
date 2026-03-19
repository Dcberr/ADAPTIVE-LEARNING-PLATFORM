package com.example.demo.submission.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.submission.dto.*;

public interface SubmissionService {

    SubmissionResponse submit(UUID userId, SubmitCodeRequest request);

    List<SubmissionHistoryResponse> getUserSubmissions(UUID userId);

    public List<SubmissionOverviewResponse> getUserSubmissionOverview(UUID userId);

    public SubmissionDetailResponse getSubmissionDetail(UUID submissionId); 

    public List<SubmissionOverviewResponse> getProblemSubmissions(UUID problemId);

}