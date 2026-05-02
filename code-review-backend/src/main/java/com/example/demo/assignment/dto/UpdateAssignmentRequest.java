package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.assignment.entity.AssignmentStatus;
import com.example.demo.problem.dto.TestcaseDto;
// import com.example.demo.problem.dto.CreateProblemRequest.TestcaseRequest;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
public class UpdateAssignmentRequest {

    private UUID topicId;

    private String title;

    // private String description;
    
    private AssignmentStatus status;

    private Instant startTime;

    private Instant deadline;

    private Long timeLimit;

    private float maxScore;

    private int maxSubmission;

    private AssigmentDifficulty difficulty;

    private List<String> tags;

    private ProblemRequest problem;
    
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ProblemRequest {
        // private String title;

        private String description;

        private List<TestcaseDto> testcases;
    }
}
