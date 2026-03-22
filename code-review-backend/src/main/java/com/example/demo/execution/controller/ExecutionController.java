package com.example.demo.execution.controller;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.service.ExecutionService;

@RestController
@RequestMapping("/execution")
@RequiredArgsConstructor
public class ExecutionController {

    private final ExecutionService executionService;

    @PostMapping("/judge")
    public ApiResponse<RunCodeResponse> judge(
            @RequestBody RunTestcaseRequest request
    ) {

        return ApiResponse.success(
                executionService.runByTestcase(request)
        );
    }
}