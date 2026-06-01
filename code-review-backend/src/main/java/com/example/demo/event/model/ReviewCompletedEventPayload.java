package com.example.demo.event.model;

import java.time.Instant;
import java.util.UUID;

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
public class ReviewCompletedEventPayload {

    private UUID reviewId;

    private UUID submissionId;

    private UUID problemId;

    private UUID userId;

    private String language;

    private String summary;

    private Instant createdAt;
}

