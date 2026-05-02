package com.example.demo.document.dto;

import org.springframework.web.multipart.MultipartFile;

import lombok.Data;

@Data
public class UpdateDocumentRequest {

    private String title;

    private String description;

    private MultipartFile file;
}
