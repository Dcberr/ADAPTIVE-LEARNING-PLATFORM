package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.UUID;

import lombok.Data;

@Data
public class CreateAssignmentRequest {

    private UUID topicId;

    private String title;

    private String description;

    private Instant deadline;
}
