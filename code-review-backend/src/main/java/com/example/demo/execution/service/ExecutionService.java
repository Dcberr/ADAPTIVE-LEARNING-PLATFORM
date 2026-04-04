package com.example.demo.execution.service;

import com.example.demo.execution.dto.RunCodeRequest;
import com.example.demo.execution.dto.RunCodeResponse;
import com.example.demo.execution.dto.RunTestcaseRequest;

public interface ExecutionService {

    public RunCodeResponse runByTestcase(RunTestcaseRequest request);

    public RunCodeResponse runByCustomInput(RunCodeRequest request);

}