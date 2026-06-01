package com.example.demo.event;

public final class EventType {

    public static final String ASSIGNMENT_CREATED = "assignment.created";
    public static final String ASSIGNMENT_UPDATED = "assignment.updated";
    public static final String ASSIGNMENT_DELETED = "assignment.deleted";
    public static final String SUBMISSION_CREATED = "submission.created";
    public static final String REVIEW_COMPLETED = "review.completed";

    private EventType() {
    }
}

