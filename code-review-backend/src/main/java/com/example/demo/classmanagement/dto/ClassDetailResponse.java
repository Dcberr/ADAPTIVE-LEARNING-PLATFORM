package com.example.demo.classmanagement.dto;

import java.util.List;

import com.example.demo.user.dto.UserResponse;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ClassDetailResponse {

    private String name;

    private String instructorName;

    private int enrolledStudentsCount;
    
    private List<UserResponse> enrolledStudents;
    
    private String createdAt;

    private String status;

    private String schedule;

    private String imageUrl;
}
