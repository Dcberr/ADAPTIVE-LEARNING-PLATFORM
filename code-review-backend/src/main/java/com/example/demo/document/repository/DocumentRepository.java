package com.example.demo.document.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.document.entity.Document;

@Repository
public interface DocumentRepository
        extends JpaRepository<Document, UUID> {

    List<Document> findByTopicId(UUID topicId);

}
