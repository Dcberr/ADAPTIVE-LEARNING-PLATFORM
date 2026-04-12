package com.example.demo.assignment.entity;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "assignments")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Assignment {

    @Id
    @GeneratedValue
    private UUID id;

    private UUID topicId;

    private String title;

    private String description;

    private Instant startTime;

    private Instant deadline;

    private Long timeLimit;

    private float maxScore;

    private int maxSubmission;

    private List<String> tags;

    private Instant createdAt;

    @Enumerated(EnumType.STRING)
    private AssigmentDifficulty difficulty; 

    @Enumerated(EnumType.STRING)
    private AssignmentStatus status;
}