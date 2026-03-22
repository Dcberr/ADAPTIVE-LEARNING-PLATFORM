package com.example.demo.classmanagement.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ClassDetailResponse {

    private String name;

    private String instructorName;

    private int enrolledStudentsCount;
    
    private String createdAt;

    private String status;

    private String schedule;
}
