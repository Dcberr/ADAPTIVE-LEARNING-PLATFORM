package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.assignment.entity.AssignmentStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentDetailResponse {

    private UUID id;

    private String title;

    private Instant deadline;

    private AssigmentDifficulty difficulty;

    private Instant startTime;

    private Long timeLimit;

    private float maxScore;

    private int maxSubmission;

    private Integer attemptsUsed;

    private Integer remainingSubmission;

    private List<String> tags;

    private AssignmentStatus status;

}
