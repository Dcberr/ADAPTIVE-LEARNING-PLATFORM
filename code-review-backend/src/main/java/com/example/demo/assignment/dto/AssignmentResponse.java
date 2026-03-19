package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentResponse {

    private UUID id;

    private UUID topicId;

    private String title;

    private String description;

    private Instant deadline;

}