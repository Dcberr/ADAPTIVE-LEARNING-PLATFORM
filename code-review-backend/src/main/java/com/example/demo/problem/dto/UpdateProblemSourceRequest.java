package com.example.demo.problem.dto;

import java.util.UUID;

import lombok.Data;

@Data
public class UpdateProblemSourceRequest {

    private UUID problemId;

    private String externalId;
}
