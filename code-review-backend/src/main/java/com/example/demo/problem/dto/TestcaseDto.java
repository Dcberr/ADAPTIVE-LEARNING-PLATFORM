package com.example.demo.problem.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TestcaseDto {

    private String input;
    private String expectedOutput;
    private boolean isHidden;
    private String explanation;
}
