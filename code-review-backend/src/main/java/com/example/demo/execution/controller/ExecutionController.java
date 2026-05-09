package com.example.demo.execution.controller;

import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.execution.dto.RunCodeRequest;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;
import com.example.demo.execution.service.ExecutionService;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Execution", description = "Code execution & judging APIs")
@RestController
@RequestMapping("/execution")
@RequiredArgsConstructor
public class ExecutionController {

    private final ExecutionService executionService;

    @Operation(summary = "Run and judge code against testcases")
    @PostMapping("/judge")
    public ApiResponse<RunCodeResponse> judge(
            @RequestBody RunTestcaseRequest request
    ) {
        return ApiResponse.success(
                executionService.runByTestcase(request)
        );
    }

    @Operation(summary = "Run code without judging")
    @Hidden
    @PostMapping("/run")
    public ApiResponse<RunCodeResponse> run(
            @RequestBody RunCodeRequest request
    ) {
        return ApiResponse.success(
                executionService.runByCustomInput(request)
        );  
    }
}
