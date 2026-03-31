package com.example.demo.classmanagement.dto;

import org.springframework.web.multipart.MultipartFile;

import lombok.Data;

@Data
public class CreateClassRequest {

    private String name;

    private String description;

    private MultipartFile image;

    private String schedule;
}
