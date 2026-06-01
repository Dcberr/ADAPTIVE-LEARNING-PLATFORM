package com.example.demo.event;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.assignment.entity.Assignment;
import com.example.demo.assignment.repository.AssignmentRepository;
import com.example.demo.classmanagement.entity.ClassEnrollment;
import com.example.demo.classmanagement.repository.ClassEnrollmentRepository;
import com.example.demo.classmanagement.repository.ClassRepository;
import com.example.demo.event.model.AssignmentEventPayload;
import com.example.demo.event.model.EventEnvelope;
import com.example.demo.event.model.ReviewCompletedEventPayload;
import com.example.demo.event.model.SubmissionCreatedEventPayload;
import com.example.demo.notification.service.NotificationService;
import com.example.demo.topic.entity.Topic;
import com.example.demo.topic.repository.TopicRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class KafkaWorkflowConsumer {

    private final ObjectMapper objectMapper;
    private final NotificationService notificationService;
    private final AssignmentRepository assignmentRepository;
    private final TopicRepository topicRepository;
    private final ClassRepository classRepository;
    private final ClassEnrollmentRepository classEnrollmentRepository;

    @KafkaListener(
            topics = "${app.kafka.topics.assignment}",
            groupId = "${app.kafka.consumer-group:code-review-backend}"
    )
    @Transactional
    public void consumeAssignmentEvent(String message) {
        EventEnvelope envelope = readEnvelope(message);
        AssignmentEventPayload payload = parsePayload(envelope.getPayload(), AssignmentEventPayload.class);

        Set<UUID> recipients = resolveClassParticipants(payload.getTopicId(), true);
        String actionLabel = payload.getAction() != null ? payload.getAction() : "updated";

        notificationService.createNotifications(
                recipients,
                envelope.getEventId(),
                envelope.getEventType(),
                "Assignment " + actionLabel,
                "Assignment \"" + payload.getTitle() + "\" was " + actionLabel + ".",
                "ASSIGNMENT",
                payload.getAssignmentId(),
                payload
        );
    }

    @KafkaListener(
            topics = "${app.kafka.topics.submission}",
            groupId = "${app.kafka.consumer-group:code-review-backend}"
    )
    @Transactional
    public void consumeSubmissionEvent(String message) {
        EventEnvelope envelope = readEnvelope(message);
        SubmissionCreatedEventPayload payload = parsePayload(envelope.getPayload(), SubmissionCreatedEventPayload.class);

        if (payload.getAssignmentId() == null) {
            return;
        }

        Set<UUID> recipients = resolveClassParticipantsFromAssignment(payload.getAssignmentId(), false);
        notificationService.createNotifications(
                recipients,
                envelope.getEventId(),
                envelope.getEventType(),
                "New assignment submission",
                "A student submitted code for assignment " + payload.getAssignmentId() + ".",
                "SUBMISSION",
                payload.getSubmissionId(),
                payload
        );
    }

    @KafkaListener(
            topics = "${app.kafka.topics.review}",
            groupId = "${app.kafka.consumer-group:code-review-backend}"
    )
    @Transactional
    public void consumeReviewEvent(String message) {
        EventEnvelope envelope = readEnvelope(message);
        ReviewCompletedEventPayload payload = parsePayload(envelope.getPayload(), ReviewCompletedEventPayload.class);

        if (payload.getUserId() == null) {
            return;
        }

        notificationService.createNotifications(
                List.of(payload.getUserId()),
                envelope.getEventId(),
                envelope.getEventType(),
                "Code review ready",
                "Your AI code review is ready for submission " + payload.getSubmissionId() + ".",
                "REVIEW",
                payload.getReviewId(),
                payload
        );
    }

    private EventEnvelope readEnvelope(String message) {
        try {
            return objectMapper.readValue(message, EventEnvelope.class);
        } catch (Exception ex) {
            log.error("Failed to deserialize Kafka event envelope: {}", message, ex);
            throw new IllegalStateException("Invalid Kafka event payload", ex);
        }
    }

    private <T> T parsePayload(JsonNode payload, Class<T> payloadType) {
        try {
            return objectMapper.treeToValue(payload, payloadType);
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to deserialize event payload to " + payloadType.getSimpleName(), ex);
        }
    }

    private Set<UUID> resolveClassParticipantsFromAssignment(UUID assignmentId, boolean includeStudents) {
        if (assignmentId == null) {
            return Set.of();
        }

        Assignment assignment = assignmentRepository.findByIdAndDeletedAtIsNull(assignmentId).orElse(null);
        if (assignment == null) {
            return Set.of();
        }

        return resolveClassParticipants(assignment.getTopicId(), includeStudents);
    }

    private Set<UUID> resolveClassParticipants(UUID topicId, boolean includeStudents) {
        if (topicId == null) {
            return Set.of();
        }

        Topic topic = topicRepository.findByIdAndDeletedAtIsNull(topicId).orElse(null);
        if (topic == null) {
            return Set.of();
        }

        LinkedHashSet<UUID> recipients = new LinkedHashSet<>();
        classRepository.findByIdAndDeletedAtIsNull(topic.getClassId())
                .map(clazz -> clazz.getInstructorId())
                .ifPresent(recipients::add);

        if (includeStudents) {
            classEnrollmentRepository.findByClassId(topic.getClassId()).stream()
                    .map(ClassEnrollment::getStudentId)
                    .forEach(recipients::add);
        }

        return recipients;
    }
}
