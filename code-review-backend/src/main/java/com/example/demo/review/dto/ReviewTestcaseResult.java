package com.example.demo.review.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewTestcaseResult {

    private String input;

    private String expectedOutput;

    private String actualOutput;

    private boolean passed;
}