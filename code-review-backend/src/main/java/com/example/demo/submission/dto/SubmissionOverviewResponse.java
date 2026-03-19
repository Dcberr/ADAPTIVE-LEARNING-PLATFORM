package com.example.demo.submission.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class SubmissionOverviewResponse {

    private UUID submissionId;

    private String assignmentTitle;

    private String problemTitle;

    private String score;

    private String difficulty;

    private Instant deadline;

    private String status;

    private Instant submittedAt;

    private String studentName;
}