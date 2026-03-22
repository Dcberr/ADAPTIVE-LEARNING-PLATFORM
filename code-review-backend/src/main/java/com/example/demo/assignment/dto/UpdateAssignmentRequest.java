package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;

import com.example.demo.assignment.entity.AssignmentStatus;

import lombok.Data;

@Data
public class UpdateAssignmentRequest {

    private String title;

    // private String description;

    private Instant deadline;

    private List<String> tag;

    // private String title;

    private String description;

    private String difficulty;

    private AssignmentStatus status;

    // private UUID assignmentId;  

    // private String source;

    private String input;

    private String expectedOutput;

    private boolean isSample;
}
