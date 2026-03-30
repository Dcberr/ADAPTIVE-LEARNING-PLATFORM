package com.example.demo.document.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.example.demo.document.dto.CreateDocumentRequest;
import com.example.demo.document.dto.DocumentResponse;
import com.example.demo.document.dto.UploadFilleResponse;
import com.example.demo.document.entity.Document;
import com.example.demo.document.repository.DocumentRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final MinioStorageService minioStorageService;

    @Override
    public DocumentResponse create(CreateDocumentRequest request) {

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

        return documentRepository.findByTopicId(topicId)
                .stream()
                .map(this::mapDocument)
                .toList();
    }

    public ResponseEntity<Resource> download(String documentId){
            Document document = documentRepository.findById(UUID.fromString(documentId))
                    .orElseThrow(() -> new RuntimeException("Document not found"));
    
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
}
