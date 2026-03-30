package com.example.demo.document.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.service.DocumentService;
import com.example.demo.document.service.MinioStorageService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/documents")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;
    private final MinioStorageService minioStorageService;

    @PostMapping(consumes = "multipart/form-data")
        public ApiResponse<DocumentResponse> create(
                @RequestParam("file") MultipartFile file,
                @RequestParam("topicId") UUID topicId,
                @RequestParam("title") String title,
                @RequestParam("description") String description
        ) {
        CreateDocumentRequest request = new CreateDocumentRequest();
        request.setFile(file);
        request.setTopicId(topicId);
        request.setTitle(title);
        request.setDescription(description);

        return ApiResponse.success(documentService.create(request));
}

    @GetMapping("/topic/{topicId}")
    public ApiResponse<List<DocumentResponse>> getByTopic(
            @PathVariable UUID topicId
    ) {

        return ApiResponse.success(
                documentService.getDocumentsByTopic(topicId)
        );
    }

    @GetMapping("/download/{id}")
        public ResponseEntity<Resource> download(@PathVariable String id) {
        return documentService.download(id);
    }

    @GetMapping("/stream/{id}")
    public ResponseEntity<Resource> stream(
            @PathVariable String id,
            @RequestHeader(value = "Range", required = false) String range) {

        return minioStorageService.stream(id, range);
    }
}
