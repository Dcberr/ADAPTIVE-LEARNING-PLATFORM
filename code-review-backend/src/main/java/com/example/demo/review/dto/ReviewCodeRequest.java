package com.example.demo.review.dto;

import java.util.UUID;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewCodeRequest {
    private UUID problemId;
    private UUID submissionId;
    private String code;
    private String language;
}
