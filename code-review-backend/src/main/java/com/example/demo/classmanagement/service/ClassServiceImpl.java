package com.example.demo.classmanagement.service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.classmanagement.dto.ClassDetailResponse;
import com.example.demo.classmanagement.dto.ClassOverviewResponse;
import com.example.demo.classmanagement.dto.ClassResponse;
import com.example.demo.classmanagement.dto.CreateClassRequest;
import com.example.demo.classmanagement.entity.ClassEnrollment;
import com.example.demo.classmanagement.entity.ClassStatus;
import com.example.demo.classmanagement.repository.ClassEnrollmentRepository;
import com.example.demo.classmanagement.repository.ClassRepository;
import com.example.demo.document.dto.UploadFilleResponse;
import com.example.demo.document.service.MinioStorageService;
import com.example.demo.user.entity.User;
import com.example.demo.user.repository.UserRepository;
import com.example.demo.classmanagement.entity.Class;   

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ClassServiceImpl implements ClassService {

    private final ClassRepository classRepository;
    private final ClassEnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository; // For fetching instructor names
    private final MinioStorageService storageService; // For handling image uploads

    @Override
    public ClassResponse createClass(UUID instructorId, CreateClassRequest req) {

        UploadFilleResponse uploadResult = storageService.upload(req.getImage());       

        Class cls = Class.builder()
                .name(req.getName())
                .description(req.getDescription())
                .instructorId(instructorId)
                .createdAt(Instant.now())
                .status(ClassStatus.IN_PROGRESS)
                .imageUrl(uploadResult.getFileUrl())
                .schedule(req.getSchedule())    
                .build();

        

        classRepository.save(cls);

        return mapToResponse(cls);
    }

    @Override
    public List<ClassOverviewResponse> getMyClasses(UUID instructorId) {

        List<Class> classes = classRepository.findByInstructorId(instructorId); 

        return classes.stream()
                .map(this::getClassOverview)
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

        return cls == null ? null : getClassDetailResponse(cls);
    }

    private ClassOverviewResponse getClassOverview(Class cls) {

        int enrolledCount = enrollmentRepository.countByClassId(cls.getId());
        User instructor = userRepository.findById(cls.getInstructorId()).orElseThrow();
        String instructorName = instructor.getName();

        return ClassOverviewResponse.builder()
                .id(cls.getId())
                .name(cls.getName())
                .instructorName(instructorName)
                .enrolledStudentsCount(enrolledCount)
                .status(cls.getStatus())
                .imageUrl(cls.getImageUrl())
                .build();
    }

    private ClassDetailResponse getClassDetailResponse(Class cls) {

        int enrolledCount = enrollmentRepository.countByClassId(cls.getId());
        User instructor = userRepository.findById(cls.getInstructorId()).orElseThrow();
        String instructorName = instructor.getName();

        return ClassDetailResponse.builder()
                .name(cls.getName())
                .instructorName(instructorName)
                .enrolledStudentsCount(enrolledCount)
                .createdAt(cls.getCreatedAt().toString())
                .status(cls.getStatus().name())
                .schedule(cls.getSchedule())    
                .build();
    }

    private ClassResponse mapToResponse(Class cls) {

        return ClassResponse.builder()
                .id(cls.getId())
                .name(cls.getName())
                .description(cls.getDescription())
                .instructorId(cls.getInstructorId())
                .imageUrl(cls.getImageUrl())
                .build();
    }
}
