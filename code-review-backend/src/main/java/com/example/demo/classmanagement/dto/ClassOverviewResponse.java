package com.example.demo.classmanagement.dto;

import java.util.UUID;

import com.example.demo.classmanagement.entity.ClassStatus;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ClassOverviewResponse {

    private UUID id;

    private String name;

    private String instructorName;

    private int enrolledStudentsCount;
    
    private ClassStatus status;
}
