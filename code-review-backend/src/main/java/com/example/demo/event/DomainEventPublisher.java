package com.example.demo.event;

import java.util.UUID;

import org.springframework.stereotype.Component;

import com.example.demo.assignment.entity.Assignment;
import com.example.demo.event.model.AssignmentEventPayload;
import com.example.demo.event.model.ReviewCompletedEventPayload;
import com.example.demo.event.model.SubmissionCreatedEventPayload;
import com.example.demo.event.outbox.OutboxEventService;
import com.example.demo.review.entity.CodeReview;
import com.example.demo.submission.entity.Submission;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class DomainEventPublisher {

    private final KafkaTopicsProperties kafkaTopicsProperties;
    private final OutboxEventService outboxEventService;

    public void publishAssignmentCreated(Assignment assignment) {
        publishAssignmentEvent(EventType.ASSIGNMENT_CREATED, assignment, "created");
    }

    public void publishAssignmentUpdated(Assignment assignment) {
        publishAssignmentEvent(EventType.ASSIGNMENT_UPDATED, assignment, "updated");
    }

    public void publishAssignmentDeleted(Assignment assignment) {
        publishAssignmentEvent(EventType.ASSIGNMENT_DELETED, assignment, "deleted");
    }

    public void publishSubmissionCreated(Submission submission, UUID assignmentId) {
        outboxEventService.queue(
                kafkaTopicsProperties.getSubmission(),
                submission.getUserId() != null ? submission.getUserId().toString() : submission.getId().toString(),
                EventType.SUBMISSION_CREATED,
                "submission",
                submission.getId(),
                SubmissionCreatedEventPayload.builder()
                        .submissionId(submission.getId())
                        .userId(submission.getUserId())
                        .problemId(submission.getProblemId())
                        .assignmentId(assignmentId)
                        .status(submission.getStatus())
                        .language(submission.getLanguage())
                        .score(submission.getScore())
                        .submittedAt(submission.getSubmittedAt())
                        .build()
        );
    }

    public void publishReviewCompleted(CodeReview review) {
        outboxEventService.queue(
                kafkaTopicsProperties.getReview(),
                review.getUserId() != null ? review.getUserId().toString() : review.getId().toString(),
                EventType.REVIEW_COMPLETED,
                "review",
                review.getId(),
                ReviewCompletedEventPayload.builder()
                        .reviewId(review.getId())
                        .submissionId(review.getSubmissionId())
                        .problemId(review.getProblemId())
                        .userId(review.getUserId())
                        .language(review.getLanguage())
                        .summary(review.getSummary())
                        .createdAt(review.getCreatedAt())
                        .build()
        );
    }

    private void publishAssignmentEvent(String eventType, Assignment assignment, String action) {
        outboxEventService.queue(
                kafkaTopicsProperties.getAssignment(),
                assignment.getId().toString(),
                eventType,
                "assignment",
                assignment.getId(),
                AssignmentEventPayload.builder()
                        .assignmentId(assignment.getId())
                        .topicId(assignment.getTopicId())
                        .title(assignment.getTitle())
                        .status(assignment.getStatus())
                        .startTime(assignment.getStartTime())
                        .deadline(assignment.getDeadline())
                        .action(action)
                        .build()
        );
    }
}

