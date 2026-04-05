package com.example.demo.auth.controller;

import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.common.response.ApiResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Auth", description = "Authentication APIs")
@RestController
@RequestMapping("/auth")
public class AuthenticationController {

    // @Operation(summary = "Get current user info")
    // @GetMapping("/me")
    // public ApiResponse<?> me(Authentication authentication) {

    //     UUID userId = (UUID) authentication.getPrincipal();

    //     return ApiResponse.success(userId);
    // }
}
