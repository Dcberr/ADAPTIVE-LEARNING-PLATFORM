package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.UUID;

import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.assignment.entity.AssignmentStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AssignmentResponse {

    private UUID id;

    private String title;

    private Instant deadline;

    private AssigmentDifficulty difficulty;

    private Instant startTime;  

    private Instant timeLimit;  

    private float maxScore;
    
    private int maxSubmission;  

    private AssignmentStatus status;

}