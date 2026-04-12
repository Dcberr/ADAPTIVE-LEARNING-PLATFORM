package com.example.demo.review.dto;

import java.util.UUID;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewTestcaseResult {

    private UUID testcaseId;

    private String input;

    private String expectedOutput;

    private String actualOutput;

    private boolean passed;
}