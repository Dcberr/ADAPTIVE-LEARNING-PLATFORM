package com.example.demo.classmanagement.dto;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ClassDetailResponse {

    private UUID id;

    private String name;

    private String description;

    private List<UUID> studentIds;
}
