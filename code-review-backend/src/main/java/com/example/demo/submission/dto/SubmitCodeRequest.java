package com.example.demo.submission.dto;

import lombok.Data;

import java.time.Instant;
import java.util.UUID;

@Data
public class SubmitCodeRequest {

    private UUID problemId;

    private String language;

    private String code;

    private Instant startedAt;
}