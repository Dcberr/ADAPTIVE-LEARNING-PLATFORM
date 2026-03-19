package com.example.demo.auth.controller;

import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.common.response.ApiResponse;

@RestController
@RequestMapping("/auth")
public class AuthenticationController {

    @GetMapping("/me")
    public ApiResponse<?> me(Authentication authentication) {

        UUID userId = (UUID) authentication.getPrincipal();

        return ApiResponse.success(userId);
    }

}
