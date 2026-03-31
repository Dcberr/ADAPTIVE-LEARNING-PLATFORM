package com.example.demo.execution.dto;

import lombok.Data;

@Data
public class RunCodeRequest {

    private String language;

    private String code;

    private String input;

}