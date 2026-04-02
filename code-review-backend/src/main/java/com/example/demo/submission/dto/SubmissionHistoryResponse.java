package com.example.demo.submission.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.UUID;

@Data
@Builder
public class SubmissionHistoryResponse {

    private UUID id;

    private UUID problemId;

    private String status;

    private String language;

    private String code;

    private Instant submittedAt;

    private String score;
}