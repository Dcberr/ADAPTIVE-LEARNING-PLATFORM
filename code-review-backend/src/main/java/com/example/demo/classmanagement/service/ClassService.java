package com.example.demo.classmanagement.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.classmanagement.dto.*;

public interface ClassService {

    ClassResponse createClass(UUID instructorId, CreateClassRequest request);

    List<ClassResponse> getMyClasses(UUID instructorId);

    List<ClassResponse> getClassesForStudent(UUID studentId);

    void addStudent(UUID classId, UUID studentId);

    void removeStudent(UUID classId, UUID studentId);

    ClassDetailResponse getClassDetail(UUID classId);
}