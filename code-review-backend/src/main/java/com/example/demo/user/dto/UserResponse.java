package com.example.demo.user.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserResponse {

    private UUID id;

    private String email;

    private String name;

    private String userCode;

    private String picture;

    private String role;
}