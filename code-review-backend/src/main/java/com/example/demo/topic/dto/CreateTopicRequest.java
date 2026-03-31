package com.example.demo.topic.dto;

import java.util.UUID;

import lombok.Data;

@Data
public class CreateTopicRequest {

    private UUID classId;

    private String title;

    private String description;
}
