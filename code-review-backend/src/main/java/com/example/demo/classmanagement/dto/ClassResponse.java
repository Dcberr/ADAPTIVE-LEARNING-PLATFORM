package com.example.demo.classmanagement.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ClassResponse {

    private UUID id;

    private String name;

    private String description;

    private UUID instructorId;
}
