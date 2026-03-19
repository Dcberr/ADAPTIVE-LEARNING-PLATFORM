package com.example.demo.user.service;

import java.util.UUID;

import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;

public interface UserService {

    UserResponse getCurrentUser(UUID userId);

    UserResponse getUserById(UUID userId);

    UserResponse updateUser(UUID userId, UpdateUserRequest request);

}