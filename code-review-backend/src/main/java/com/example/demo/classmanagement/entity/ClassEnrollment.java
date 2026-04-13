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
@Table(
    name = "class_enrollments",
    uniqueConstraints = @UniqueConstraint(
        columnNames = {"classId", "studentId"},
        name = "uk_class_student"
    )
)
public class ClassEnrollment {

    @Id
    @GeneratedValue
    private UUID id;

    private UUID classId;

    private UUID studentId;

    private Instant joinedAt;
}