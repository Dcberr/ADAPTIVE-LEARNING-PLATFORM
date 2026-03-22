package com.example.demo.document.dto;


import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UploadFilleResponse {

    private String fileUrl;

    private String type;
}