package com.example.demo.user.service;

import java.util.UUID;

import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;
import com.example.demo.user.entity.Role;

public interface UserService {

    UserResponse getCurrentUser(UUID userId);

    UserResponse getUserById(UUID userId);

    UserResponse updateUser(UUID userId, UpdateUserRequest request);

    public String generateUserCode(Role role);

}