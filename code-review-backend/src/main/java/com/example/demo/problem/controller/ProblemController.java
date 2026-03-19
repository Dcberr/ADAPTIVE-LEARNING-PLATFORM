package com.example.demo.problem.controller;

import java.util.UUID;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.problem.dto.CreateProblemRequest;
import com.example.demo.problem.dto.ProblemResponse;
import com.example.demo.problem.service.ProblemService;

@RestController
@RequestMapping("/problems")
@RequiredArgsConstructor
public class ProblemController {

    private final ProblemService problemService;

    @PostMapping
    public ApiResponse<ProblemResponse> createProblem(
            @RequestBody CreateProblemRequest request
    ) {

        return ApiResponse.success(
                problemService.createProblem(request)
        );
    }

    @GetMapping("/{problemId}")
    public ApiResponse<ProblemResponse> getProblem(
            @PathVariable UUID problemId
    ) {

        return ApiResponse.success(
                problemService.getProblem(problemId)
        );
    }
}