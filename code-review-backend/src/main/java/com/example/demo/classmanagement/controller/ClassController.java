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

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@Tag(name = "Class", description = "APIs for class management")
@RestController
@RequestMapping("/classes")
@RequiredArgsConstructor
public class ClassController {

    private final ClassService classService;

    @Operation(summary = "Create a new class")
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

    @Operation(summary = "Get classes of current user")
    @GetMapping("/me")
    public ApiResponse<List<ClassOverviewResponse>> myClasses(
            Authentication auth
    ) {
        UUID userId = (UUID) auth.getPrincipal();

        return ApiResponse.success(
                classService.getMyClasses(userId)
        );
    }

    @Operation(summary = "Add student to class")
    @PostMapping("/{classId}/students")
    public ApiResponse<?> addStudent(
            @Parameter(description = "Class ID")
            @PathVariable UUID classId,
            @RequestBody AddStudentRequest request
    ) {
        classService.addStudent(classId, request.getStudentId());
        return ApiResponse.success(null);
    }

    @Operation(summary = "Remove student from class")
    @DeleteMapping("/{classId}/students/{studentId}")
    public ApiResponse<?> removeStudent(
            @PathVariable UUID classId,
            @PathVariable UUID studentId
    ) {
        classService.removeStudent(classId, studentId);
        return ApiResponse.success(null);
    }

    @Operation(summary = "Get class detail")
    @GetMapping("/{classId}")
    public ApiResponse<ClassDetailResponse> classDetail(
            @PathVariable UUID classId
    ) {
        return ApiResponse.success(
                classService.getClassDetail(classId)
        );
    }
}