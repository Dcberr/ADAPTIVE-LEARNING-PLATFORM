package com.example.demo.document.dto;

import java.util.UUID;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class DocumentResponse {

    private UUID id;

    private String title;

    private String description;

    private String fileUrl;

    private String type;
}
