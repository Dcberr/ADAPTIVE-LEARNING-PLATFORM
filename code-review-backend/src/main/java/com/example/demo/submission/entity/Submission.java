package com.example.demo.submission.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import com.example.demo.execution.dto.TestcaseResult;

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

    @Enumerated(EnumType.STRING)
    private SubmissionStatus status = SubmissionStatus.IN_PROGRESS;

    private Long runtime;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<TestcaseResult> testcaseResults;

    private Integer passedTestcases;

    private Integer totalTestcases;

    @Column(name = "started_at")
    private Instant startedAt;  

    @Column(name = "submitted_at")
    private Instant submittedAt;

    private String score;  
}