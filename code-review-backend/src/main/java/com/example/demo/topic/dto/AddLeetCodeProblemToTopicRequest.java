package com.example.demo.topic.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import lombok.Data;

@Data
public class AddLeetCodeProblemToTopicRequest {

    private UUID problemId;

    private String title;

    private Instant startTime;

    private Instant deadline;

    private Long timeLimit;

    private float maxScore;

    private int maxSubmission;

    private List<String> tags;
}
