package com.example.demo.submission.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

import com.example.demo.submission.entity.SubmissionStatus;


@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class SubmissionResponse {

    private UUID submissionId;

    private SubmissionStatus status;

    private Instant startedAt;

    private Instant submittedAt;
    
    private String score;

    private String studentName;
}