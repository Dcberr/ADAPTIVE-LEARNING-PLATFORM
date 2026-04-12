package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.example.demo.assignment.entity.AssigmentDifficulty;
import com.example.demo.problem.dto.CreateProblemRequest.TestcaseRequest;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class CreateAssignmentRequest {

    private UUID topicId;

    private String title;

    // private String description;

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

        private String problemConstraint;

        private Map<String, String> starterCodes;

        private List<TestcaseRequest> testcases;
    }

}
