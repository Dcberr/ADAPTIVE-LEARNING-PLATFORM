package com.example.demo.problem.service;

import java.util.UUID;

import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;

public interface ProblemService {

    ProblemResponse createProblem(CreateProblemRequest request);

    ProblemResponse getProblem(UUID problemId);

}