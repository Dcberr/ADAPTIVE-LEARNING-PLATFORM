package com.example.demo.classmanagement.service;

import java.util.List;
import java.util.UUID;

import com.example.demo.classmanagement.dto.*;
import com.example.demo.user.dto.UserResponse;

public interface ClassService {

    ClassResponse createClass(UUID instructorId, CreateClassRequest request);

    ClassResponse updateClass(UUID classId, UpdateClassRequest request);

    List<ClassOverviewResponse> getClassesForInstructor(UUID instructorId);

    List<ClassOverviewResponse> getClassesForStudent(UUID studentId);

    List<ClassOverviewResponse> getMyClasses(UUID userId);

    void addStudentToClassByUserCode(UUID classId, String userCode);

    void addStudent(UUID classId, UUID studentId);

    void removeStudent(UUID classId, UUID studentId);

    void removeStudentFromClassByUserCode(UUID classId, String userCode);

    ClassDetailResponse getClassDetail(UUID classId);

    List<UserResponse> getEnrolledStudents(UUID classId);

    void deleteClass(UUID classId);
}
