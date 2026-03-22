package com.example.demo.submission.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "submissions")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Submission {

    @Id
    @GeneratedValue
    private UUID id;

    private UUID userId;

    private UUID problemId;

    private String language;

    @Column(columnDefinition = "TEXT")
    private String code;

    private String status;

    private Long runtime;

    private Integer passedTestcases;

    private Integer totalTestcases;

    private Instant createdAt;

    private String score;  
}