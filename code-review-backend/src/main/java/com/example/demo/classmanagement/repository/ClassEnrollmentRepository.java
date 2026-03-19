package com.example.demo.classmanagement.repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.classmanagement.entity.ClassEnrollment;

@Repository
public interface ClassEnrollmentRepository
        extends JpaRepository<ClassEnrollment, UUID> {

    List<ClassEnrollment> findByClassId(UUID classId);

    List<ClassEnrollment> findByStudentId(UUID studentId);

    Optional<ClassEnrollment> findByClassIdAndStudentId(
            UUID classId,
            UUID studentId
    );
}