package com.example.demo.user.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;
import com.example.demo.user.entity.Role;
import com.example.demo.user.service.UserService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "User", description = "APIs for user management")
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "Get current user profile")
    @GetMapping("/me")
    public ApiResponse<UserResponse> me(Authentication authentication) {

        UUID userId = (UUID) authentication.getPrincipal();

        return ApiResponse.success(
                userService.getCurrentUser(userId)
        );
    }

    @Operation(summary = "Get user by ID")
    @GetMapping("/{id}")
    public ApiResponse<UserResponse> getUser(
            @Parameter(description = "User ID")
            @PathVariable UUID id
    ) {
        return ApiResponse.success(
                userService.getUserById(id)
        );
    }

    @Operation(summary = "Update current user profile")
    @PutMapping("/me")
    public ApiResponse<UserResponse> updateProfile(
            Authentication authentication,
            @RequestBody UpdateUserRequest request
    ) {
        UUID userId = (UUID) authentication.getPrincipal();

        return ApiResponse.success(
                userService.updateUser(userId, request)
        );
    }

    @Operation(summary = "Get user by user code")
    @GetMapping("/code/{userCode}")
    public ApiResponse<UserResponse> getStudentByUserCode(
            @PathVariable String userCode
    ) {
        return ApiResponse.success(
                userService.getStudentByUserCode(userCode)
        );
    }

    @Operation(summary = "Get all users by role")
        @GetMapping("/role/{role}")
        public ApiResponse<List<UserResponse>> getAllUsersByRole(
                @Parameter(description = "User role")
                @PathVariable String role
        ) {
        return ApiResponse.success(
                userService.getAllUsersByRole(Role.valueOf(role.toUpperCase()))
        );
    }
}