package com.example.demo.event.model;

import java.time.Instant;
import java.util.UUID;

import com.example.demo.assignment.entity.AssignmentStatus;

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
public class AssignmentEventPayload {

    private UUID assignmentId;

    private UUID topicId;

    private String title;

    private AssignmentStatus status;

    private Instant startTime;

    private Instant deadline;

    private String action;
}

