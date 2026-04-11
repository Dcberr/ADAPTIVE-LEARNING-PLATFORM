package com.example.demo.classmanagement.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.classmanagement.dto.*;

public interface ClassService {

    ClassResponse createClass(UUID instructorId, CreateClassRequest request);

    List<ClassOverviewResponse> getClassesForInstructor(UUID instructorId);

    List<ClassOverviewResponse> getClassesForStudent(UUID studentId);

    List<ClassOverviewResponse> getMyClasses(UUID userId);

    void addStudent(UUID classId, UUID studentId);

    void removeStudent(UUID classId, UUID studentId);

    ClassDetailResponse getClassDetail(UUID classId);

    
}