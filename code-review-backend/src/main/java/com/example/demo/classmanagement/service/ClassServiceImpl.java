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
import com.example.demo.user.dto.UserResponse;
import com.example.demo.user.entity.Role;
import com.example.demo.user.entity.User;
import com.example.demo.user.repository.UserRepository;
import com.example.demo.classmanagement.entity.Class;
import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;   

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class ClassServiceImpl implements ClassService {

    private final ClassRepository classRepository;
    private final ClassEnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository; // For fetching instructor names
    private final MinioStorageService storageService; // For handling image uploads

    @Override
    public ClassResponse createClass(UUID instructorId, CreateClassRequest req) {
        UploadFilleResponse uploadResult = null;
        if (req.getImage() != null && !req.getImage().isEmpty()) {
            uploadResult = storageService.upload(req.getImage()); 
        }

        Class cls = Class.builder()
                .name(req.getName())
                .description(req.getDescription())
                .instructorId(instructorId)
                .createdAt(Instant.now())
                .status(ClassStatus.IN_PROGRESS)
                .imageUrl(uploadResult != null ? uploadResult.getFileUrl() : null)
                .schedule(req.getSchedule())    
                .build();

        classRepository.save(cls);

        return mapToResponse(cls);
    }

    @Override
    public List<ClassOverviewResponse> getClassesForInstructor(UUID instructorId) {

        List<Class> classes = classRepository.findByInstructorId(instructorId);

        return classes.stream()
                .map(this::getClassOverview)
                .toList();
    }

    @Override
    public List<ClassOverviewResponse> getClassesForStudent(UUID studentId) {

        List<ClassEnrollment> enrollments =
                enrollmentRepository.findByStudentId(studentId);

        return enrollments.stream()
                .map(e -> classRepository.findById(e.getClassId()).orElseThrow())
                .map(this::getClassOverview)
                .toList();
    }

    @Override
    public List<ClassOverviewResponse> getMyClasses(UUID userId) {
        User user = userRepository.findById(userId).orElseThrow();
        if (user.getRole() == Role.INSTRUCTOR) {
            return getClassesForInstructor(userId);
        } else {
            return getClassesForStudent(userId);
        }
    }

    @Override
    public void addStudent(UUID classId, UUID studentId) {
        // Check if student is already enrolled in the class
        if (enrollmentRepository.findByClassIdAndStudentId(classId, studentId).isPresent()) {
            throw new AppException(ErrorCode.STUDENT_ALREADY_ENROLLED);
        }

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

        Class cls = classRepository.findById(classId).orElseThrow(() -> new RuntimeException("Class not found"));
        
        ClassDetailResponse detailResponse = getClassDetailResponse(cls);

        return detailResponse;
    }

    private ClassOverviewResponse getClassOverview(Class cls) {

        int enrolledCount = enrollmentRepository.countByClassId(cls.getId());
        User instructor = userRepository.findById(cls.getInstructorId()).orElseThrow(() -> new RuntimeException("Instructor not found"));
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

        List<UserResponse> enrolledStudents = enrollmentRepository
                .findByClassId(cls.getId())
                .stream()
                .map(e -> {
                    User student = userRepository.findById(e.getStudentId()).orElseThrow();
                    return UserResponse.builder()
                            .id(student.getId())
                            .name(student.getName())
                            .email(student.getEmail())
                            .picture(student.getPicture())
                            .role(student.getRole().name())
                            .build();
                })
                .toList();

        log.info(enrolledStudents.toString());

        return ClassDetailResponse.builder()
                .name(cls.getName())
                .instructorName(instructorName)
                .enrolledStudentsCount(enrolledCount)
                .createdAt(cls.getCreatedAt().toString())
                .enrolledStudents(enrolledStudents)
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

    @Override
    public void addStudentToClassByUserCode(UUID classId, String userCode) {
        User student = userRepository.findByUserCode(userCode)
                .orElseThrow(() -> new RuntimeException("Student not found with user code: " + userCode));

        addStudent(classId, student.getId());
    }

    @Override
    public void removeStudentFromClassByUserCode(UUID classId, String userCode) {
        User student = userRepository.findByUserCode(userCode)
                .orElseThrow(() -> new RuntimeException("Student not found with user code: " + userCode));

        removeStudent(classId, student.getId());
    }

    @Override
    public List<UserResponse> getEnrolledStudents(UUID classId) {
        List<ClassEnrollment> enrollments = enrollmentRepository.findByClassId(classId);

        return enrollments.stream()
                .map(e -> userRepository.findById(e.getStudentId()).orElseThrow())
                .map(student -> UserResponse.builder()
                        .id(student.getId())
                        .name(student.getName())
                        .email(student.getEmail())
                        .picture(student.getPicture())
                        .userCode(student.getUserCode())
                        .role(student.getRole().name())
                        .build())
                .toList();
    }
}
