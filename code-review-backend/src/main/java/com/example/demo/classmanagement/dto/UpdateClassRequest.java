package com.example.demo.classmanagement.dto;

import org.springframework.web.multipart.MultipartFile;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class UpdateClassRequest {

    private String name;

    private String description;

    private String schedule;

    @Schema(type = "string", format = "binary")
    private MultipartFile image;
}
