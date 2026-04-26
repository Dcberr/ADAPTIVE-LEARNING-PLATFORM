package com.example.demo.problem.entity;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.MapKeyColumn;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(
    name = "problems",
    uniqueConstraints = {
        @UniqueConstraint(columnNames = {"source", "externalId"})
    }
)
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Problem {

    @Id
    @GeneratedValue
    private UUID id;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    private String difficulty;

    @Column(columnDefinition = "TEXT")
    private String problemConstraint;

    // =========================
    // TYPE & SOURCE
    // =========================
    @Enumerated(EnumType.STRING)
    private ProblemType type; // MANUAL | LEETCODE

    private String source; // LEETCODE | SYSTEM

    private String externalId; // leetcode slug hoặc id

    // =========================
    // CODE TEMPLATE
    // =========================
    @ElementCollection
    @CollectionTable(name = "problem_starter_codes")
    @MapKeyColumn(name = "language")
    @Column(name = "starter_code", columnDefinition = "TEXT")
    private Map<String, String> starterCodes;

    private Instant createdAt;
}