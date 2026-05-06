package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.UUID;

import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.assignment.entity.AssignmentStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentDeadlineResponse {

    private UUID id;

    private UUID topicId;

    private String topicTitle;

    private String title;

    private Instant startTime;

    private Instant deadline;

    private AssigmentDifficulty difficulty;

    private AssignmentStatus status;
}
