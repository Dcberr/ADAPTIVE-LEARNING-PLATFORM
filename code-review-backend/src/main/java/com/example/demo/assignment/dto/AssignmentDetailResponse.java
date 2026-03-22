package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentDetailResponse {

    private UUID id;

    private String title;

    private String description;

    private Instant deadline;

    private List<UUID> problemIds;

}