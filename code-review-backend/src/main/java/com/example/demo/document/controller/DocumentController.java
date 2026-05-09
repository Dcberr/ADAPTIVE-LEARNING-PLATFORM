package com.example.demo.document.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.dto.UpdateDocumentRequest;
import com.example.demo.document.service.DocumentService;
import com.example.demo.document.service.MinioStorageService;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@Tag(name = "Document", description = "APIs for document management")
@RestController
@RequestMapping("/documents")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;
    private final MinioStorageService minioStorageService;

    @Operation(summary = "Upload document (PDF, video, etc.)")
    @PostMapping(consumes = "multipart/form-data")
    public ApiResponse<DocumentResponse> create(
            @Parameter(description = "File to upload")
            @RequestParam("file") MultipartFile file,

            @Parameter(description = "Topic ID")
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

    @Operation(summary = "Get documents by topic")
    @GetMapping("/topic/{topicId}")
    public ApiResponse<List<DocumentResponse>> getByTopic(
            @Parameter(description = "Topic ID")
            @PathVariable UUID topicId
    ) {
        return ApiResponse.success(
                documentService.getDocumentsByTopic(topicId)
        );
    }

    // @Operation(summary = "Get document detail")
    // @GetMapping("/{documentId}")
    // public ApiResponse<DocumentResponse> getById(
    //         @Parameter(description = "Document ID")
    //         @PathVariable UUID documentId
    // ) {
    //     return ApiResponse.success(documentService.getDocumentById(documentId));
    // }

    @Operation(summary = "Update document")
    @PutMapping(value = "/{documentId}", consumes = "multipart/form-data")
    public ApiResponse<DocumentResponse> update(
            @Parameter(description = "Document ID")
            @PathVariable UUID documentId,
            @RequestParam(value = "title", required = false) String title,
            @RequestParam(value = "description", required = false) String description,
            @RequestParam(value = "file", required = false) MultipartFile file
    ) {
        UpdateDocumentRequest request = new UpdateDocumentRequest();
        request.setTitle(title);
        request.setDescription(description);
        request.setFile(file);

        return ApiResponse.success(documentService.update(documentId, request));
    }

    @Operation(summary = "Download document (inline preview)")
    @GetMapping("/download/{id}")
    public ResponseEntity<Resource> download(
            @Parameter(description = "Document ID")
            @PathVariable String id
    ) {
        return documentService.download(id);
    }

    @Operation(summary = "Stream video document (supports Range header)")
    @Hidden
    @GetMapping("/stream/{id}")
    public ResponseEntity<Resource> stream(
            @Parameter(description = "Document ID")
            @PathVariable String id,
            @Parameter(description = "Range header for streaming")
            @RequestHeader(value = "Range", required = false) String range
    ) {
        return minioStorageService.stream(id, range);
    }

    @Operation(summary = "Soft delete document")
    @DeleteMapping("/{documentId}")
    public ApiResponse<?> delete(
            @Parameter(description = "Document ID")
            @PathVariable UUID documentId
    ) {
        documentService.delete(documentId);
        return ApiResponse.success(null);
    }
}
