package com.example.demo.classmanagement.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.classmanagement.dto.AddStudentRequest;
import com.example.demo.classmanagement.dto.ClassDetailResponse;
import com.example.demo.classmanagement.dto.ClassOverviewResponse;
import com.example.demo.classmanagement.dto.ClassResponse;
import com.example.demo.classmanagement.dto.CreateClassRequest;
import com.example.demo.classmanagement.service.ClassService;
import com.example.demo.common.response.ApiResponse;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/classes")
@RequiredArgsConstructor
public class ClassController {

    private final ClassService classService;

    @PostMapping
    public ApiResponse<ClassResponse> createClass(
            Authentication auth,
            @ModelAttribute CreateClassRequest request
    ) {

        UUID instructorId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                classService.createClass(instructorId, request)
        );
    }

    @GetMapping("/me")
    public ApiResponse<List<ClassOverviewResponse>> myClasses(
            Authentication auth
    ) {

        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                classService.getMyClasses(userId)
        );
    }

    @PostMapping("/{classId}/students")
    public ApiResponse<?> addStudent(
            @PathVariable UUID classId,
            @RequestBody AddStudentRequest request
    ) {

        classService.addStudent(classId, request.getStudentId());

        return ApiResponse.success(null);
    }

    @DeleteMapping("/{classId}/students/{studentId}")
    public ApiResponse<?> removeStudent(
            @PathVariable UUID classId,
            @PathVariable UUID studentId
    ) {

        classService.removeStudent(classId, studentId);

        return ApiResponse.success(null);
    }

    @GetMapping("/{classId}")
    public ApiResponse<ClassDetailResponse> classDetail(
            @PathVariable UUID classId
    ) {

        return ApiResponse.success(
                classService.getClassDetail(classId)
        );
    }
}