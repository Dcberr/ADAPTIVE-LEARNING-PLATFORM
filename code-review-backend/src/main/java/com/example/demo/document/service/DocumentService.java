package com.example.demo.document.service;

import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;

import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;

public interface DocumentService {

    DocumentResponse create(CreateDocumentRequest request);

    List<DocumentResponse> getDocumentsByTopic(UUID topicId);

    public ResponseEntity<Resource> download(String documentId);

}
