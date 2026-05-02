package com.example.demo.document.service;

import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;

import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.dto.UpdateDocumentRequest;

public interface DocumentService {

    DocumentResponse create(CreateDocumentRequest request);

    List<DocumentResponse> getDocumentsByTopic(UUID topicId);

    DocumentResponse getDocumentById(UUID documentId);

    DocumentResponse update(UUID documentId, UpdateDocumentRequest request);

    void delete(UUID documentId);

    ResponseEntity<Resource> download(String documentId);

}
