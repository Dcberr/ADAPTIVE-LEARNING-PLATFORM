package com.example.demo.topic.dto;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class TopicOverviewResponse {

    private List<UUID> ids;
    // private String title;
}