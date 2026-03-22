package com.example.demo.user.controller;

import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import lombok.RequiredArgsConstructor;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;
import com.example.demo.user.service.UserService;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    public ApiResponse<UserResponse> me(Authentication authentication) {

        UUID userId = (UUID) authentication.getPrincipal();

        return ApiResponse.success(
                userService.getCurrentUser(userId)
        );
    }

    @GetMapping("/{id}")
    public ApiResponse<UserResponse> getUser(
            @PathVariable UUID id
    ) {

        return ApiResponse.success(
                userService.getUserById(id)
        );
    }

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