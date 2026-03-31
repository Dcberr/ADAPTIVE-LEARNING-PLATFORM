package com.example.demo.document.dto;

import java.util.UUID;

import org.springframework.web.multipart.MultipartFile;

import lombok.Data;

@Data
public class CreateDocumentRequest {

    private UUID topicId;

    private String title;

    private String description;

    private MultipartFile file;

    // private String type; // PDF | VIDEO
}
