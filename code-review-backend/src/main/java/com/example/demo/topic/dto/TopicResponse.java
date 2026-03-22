package com.example.demo.topic.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class TopicResponse {

    private UUID id;

    private UUID classId;

    private String title;

    private String description;
}
