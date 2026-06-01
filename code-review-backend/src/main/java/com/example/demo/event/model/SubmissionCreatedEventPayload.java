package com.example.demo.event.model;

import java.time.Instant;
import java.util.UUID;

import com.example.demo.submission.entity.SubmissionStatus;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionCreatedEventPayload {

    private UUID submissionId;

    private UUID userId;

    private UUID problemId;

    private UUID assignmentId;

    private SubmissionStatus status;

    private String language;

    private String score;

    private Instant submittedAt;
}

