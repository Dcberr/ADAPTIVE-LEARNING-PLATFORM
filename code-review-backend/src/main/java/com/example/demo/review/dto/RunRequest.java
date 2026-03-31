package com.example.demo.review.dto;

import java.util.List;

import com.example.demo.assignment.entity.Assignment;
import com.example.demo.problem.entity.Testcase;
import com.example.demo.submission.entity.Submission;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Data
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RunRequest {
    // private String languageId;
    // private String sourceCode;
    private Assignment assignment;
    private Submission submission;
    private List<Testcase> testcase;
    // private String input;
    private Integer cputime = 10;      
    private Integer memorylimit = 2000000;  
}
