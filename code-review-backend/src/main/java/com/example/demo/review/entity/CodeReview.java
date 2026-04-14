package com.example.demo.review.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "code_reviews")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CodeReview {

    @Id
    @GeneratedValue
    private UUID id;

    private UUID submissionId;

    private UUID problemId;

    private UUID userId;

    private String language;

    @Column(columnDefinition = "TEXT")
    private String summary;

    @Column(columnDefinition = "TEXT")
    private String detail;

    @Column(columnDefinition = "TEXT")
    private String reviewItemsJson;

    private Instant createdAt;
}