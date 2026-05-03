package com.example.demo.topic.dto;

import java.util.List;
import java.util.UUID;

import com.example.demo.assignment.dto.AssignmentOverviewResponse;
import com.example.demo.document.dto.DocumentResponse;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class TopicDetailResponse {

    private UUID id;
    private String title;
    private String description;

    private List<AssignmentOverviewResponse> assignments;
    private List<DocumentResponse> documents;
}
