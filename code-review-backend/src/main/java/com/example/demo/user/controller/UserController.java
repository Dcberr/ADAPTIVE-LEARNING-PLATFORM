package com.example.demo.user.controller;

import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;
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
}