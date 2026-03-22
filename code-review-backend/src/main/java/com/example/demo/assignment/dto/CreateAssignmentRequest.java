package com.example.demo.assignment.dto;

import java.time.Instant;
import java.util.List;
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

    private Instant deadline;

    private AssigmentDifficulty difficulty;

    private ProblemRequest problem;
    
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ProblemRequest {
        // private String title;

        private String description;

        private List<TestcaseRequest> testcases;
    }

}
