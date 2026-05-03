package com.example.demo.assignment.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentOverviewResponse {

    private UUID id;

    private String title;
}
