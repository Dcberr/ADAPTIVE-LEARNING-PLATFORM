package com.example.demo.classmanagement.dto;

import org.springframework.web.multipart.MultipartFile;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class CreateClassRequest {

    private String name;

    private String description;

    @Schema(type = "string", format = "binary")
    private MultipartFile image;

    private String schedule;
}
