package com.example.demo.classmanagement.entity;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "class_enrollments")
public class ClassEnrollment {

    @Id
    @GeneratedValue
    private UUID id;

    private UUID classId;

    private UUID studentId;

    private Instant joinedAt;
}