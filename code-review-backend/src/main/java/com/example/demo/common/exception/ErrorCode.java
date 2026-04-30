package com.example.demo.common.exception;

import org.springframework.http.HttpStatus;

import lombok.Getter;

@Getter
public enum ErrorCode {

    USER_NOT_FOUND(HttpStatus.NOT_FOUND, "User not found"),

    CLASS_NOT_FOUND(HttpStatus.NOT_FOUND, "Class not found"),

    TOPIC_NOT_FOUND(HttpStatus.NOT_FOUND, "Topic not found"),

    ASSIGNMENT_NOT_FOUND(HttpStatus.NOT_FOUND, "Assignment not found"),

    PROBLEM_NOT_FOUND(HttpStatus.NOT_FOUND, "Problem not found"),

    SUBMISSION_NOT_FOUND(HttpStatus.NOT_FOUND, "Submission not found"),

    STUDENT_ALREADY_ENROLLED(HttpStatus.CONFLICT, "Student is already enrolled in this class"),

    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "Unauthorized"),

    FORBIDDEN(HttpStatus.FORBIDDEN, "Forbidden"),

    VALIDATION_ERROR(HttpStatus.BAD_REQUEST, "Validation error"),

    RECOMMENDATION_SERVICE_ERROR(HttpStatus.BAD_GATEWAY, "Recommendation service error"),

    INTERNAL_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "Internal server error");

    private final HttpStatus status;

    private final String message;

    ErrorCode(HttpStatus status, String message) {
        this.status = status;
        this.message = message;
    }
}
