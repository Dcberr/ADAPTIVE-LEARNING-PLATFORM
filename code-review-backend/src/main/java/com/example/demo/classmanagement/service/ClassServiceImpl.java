package com.example.demo.classmanagement.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.classmanagement.dto.ClassDetailResponse;
import com.example.demo.classmanagement.dto.ClassResponse;
import com.example.demo.classmanagement.dto.CreateClassRequest;
import com.example.demo.classmanagement.entity.ClassEnrollment;
import com.example.demo.classmanagement.repository.ClassEnrollmentRepository;
import com.example.demo.classmanagement.repository.ClassRepository;
import com.example.demo.classmanagement.entity.Class;   

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ClassServiceImpl implements ClassService {

    private final ClassRepository classRepository;
    private final ClassEnrollmentRepository enrollmentRepository;

    @Override
    public ClassResponse createClass(UUID instructorId, CreateClassRequest req) {

        Class cls = Class.builder()
                .name(req.getName())
                .description(req.getDescription())
                .instructorId(instructorId)
                .createdAt(Instant.now())
                .build();

        classRepository.save(cls);

        return mapToResponse(cls);
    }

    @Override
    public List<ClassResponse> getMyClasses(UUID instructorId) {

        return classRepository.findByInstructorId(instructorId)
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    @Override
    public List<ClassResponse> getClassesForStudent(UUID studentId) {

        List<ClassEnrollment> enrollments =
                enrollmentRepository.findByStudentId(studentId);

        return enrollments.stream()
                .map(e -> classRepository.findById(e.getClassId()).orElseThrow())
                .map(this::mapToResponse)
                .toList();
    }

    @Override
    public void addStudent(UUID classId, UUID studentId) {

        ClassEnrollment enrollment =
                ClassEnrollment.builder()
                        .classId(classId)
                        .studentId(studentId)
                        .joinedAt(Instant.now())
                        .build();

        enrollmentRepository.save(enrollment);
    }

    @Override
    public void removeStudent(UUID classId, UUID studentId) {

        enrollmentRepository
                .findByClassIdAndStudentId(classId, studentId)
                .ifPresent(enrollmentRepository::delete);
    }

    @Override
    public ClassDetailResponse getClassDetail(UUID classId) {

        Class cls = classRepository.findById(classId).orElseThrow();

        List<UUID> students =
                enrollmentRepository.findByClassId(classId)
                        .stream()
                        .map(ClassEnrollment::getStudentId)
                        .toList();

        return ClassDetailResponse.builder()
                .id(cls.getId())
                .name(cls.getName())
                .description(cls.getDescription())
                .studentIds(students)
                .build();
    }

    private ClassResponse mapToResponse(Class cls) {

        return ClassResponse.builder()
                .id(cls.getId())
                .name(cls.getName())
                .description(cls.getDescription())
                .instructorId(cls.getInstructorId())
                .build();
    }
}
