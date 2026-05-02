package com.example.demo.document.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.dto.UpdateDocumentRequest;
import com.example.demo.document.dto.UploadFilleResponse;
import com.example.demo.document.entity.Document;
import com.example.demo.document.repository.DocumentRepository;
import com.example.demo.topic.repository.TopicRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final MinioStorageService minioStorageService;
    private final TopicRepository topicRepository;

    @Override
    public DocumentResponse create(CreateDocumentRequest request) {
        topicRepository.findByIdAndDeletedAtIsNull(request.getTopicId())
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));

        UploadFilleResponse uploadResponse = minioStorageService.upload(request.getFile());

        Document doc = Document.builder()
                .topicId(request.getTopicId())
                .title(request.getTitle())
                .description(request.getDescription())
                .fileUrl(uploadResponse.getFileUrl())
                .type(uploadResponse.getType())
                .createdAt(Instant.now())
                .build();

        documentRepository.save(doc);

        return mapDocument(doc);
    }

    @Override
    public List<DocumentResponse> getDocumentsByTopic(UUID topicId) {
        topicRepository.findByIdAndDeletedAtIsNull(topicId)
                .orElseThrow(() -> new AppException(ErrorCode.TOPIC_NOT_FOUND));

        return documentRepository.findByTopicIdAndDeletedAtIsNull(topicId)
                .stream()
                .map(this::mapDocument)
                .toList();
    }

    @Override
    public DocumentResponse getDocumentById(UUID documentId) {
        return mapDocument(getActiveDocument(documentId));
    }

    @Override
    public DocumentResponse update(UUID documentId, UpdateDocumentRequest request) {
        Document document = getActiveDocument(documentId);

        if (request.getTitle() != null) {
            document.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            document.setDescription(request.getDescription());
        }
        if (request.getFile() != null && !request.getFile().isEmpty()) {
            UploadFilleResponse uploadResponse = minioStorageService.upload(request.getFile());
            document.setFileUrl(uploadResponse.getFileUrl());
            document.setType(uploadResponse.getType());
        }

        documentRepository.save(document);
        return mapDocument(document);
    }

    @Override
    public void delete(UUID documentId) {
        Document document = getActiveDocument(documentId);
        document.setDeletedAt(Instant.now());
        documentRepository.save(document);
    }

    @Override
    public ResponseEntity<Resource> download(String documentId) {
            Document document = getActiveDocument(UUID.fromString(documentId));

            return minioStorageService.download(document.getFileUrl(), document.getTitle(), document.getType());
    }

    private DocumentResponse mapDocument(Document doc) {
        return DocumentResponse.builder()
                .id(doc.getId())
                .title(doc.getTitle())
                .description(doc.getDescription())
                .fileUrl(doc.getFileUrl())
                .type(doc.getType())
                .build();
    }

    private Document getActiveDocument(UUID documentId) {
        return documentRepository.findByIdAndDeletedAtIsNull(documentId)
                .orElseThrow(() -> new AppException(ErrorCode.DOCUMENT_NOT_FOUND));
    }
}
