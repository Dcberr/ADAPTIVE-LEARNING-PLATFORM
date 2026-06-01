package com.example.demo.event.outbox;

import java.time.Instant;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.event.model.EventEnvelope;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class OutboxEventService {

    private final OutboxEventRepository outboxEventRepository;
    private final ObjectMapper objectMapper;

    public void queue(String topic, String key, String eventType, String aggregateType, UUID aggregateId, Object payload) {
        try {
            UUID eventId = UUID.randomUUID();
            String serializedPayload = objectMapper.writeValueAsString(
                    EventEnvelope.builder()
                            .eventId(eventId)
                            .eventType(eventType)
                            .aggregateType(aggregateType)
                            .aggregateId(aggregateId != null ? aggregateId.toString() : null)
                            .occurredAt(Instant.now())
                            .payload(objectMapper.valueToTree(payload))
                            .build()
            );

            outboxEventRepository.save(OutboxEvent.builder()
                    .id(eventId)
                    .topic(topic)
                    .keyValue(key)
                    .eventType(eventType)
                    .aggregateType(aggregateType)
                    .aggregateId(aggregateId != null ? aggregateId.toString() : null)
                    .payload(serializedPayload)
                    .status(OutboxEventStatus.PENDING)
                    .attempts(0)
                    .createdAt(Instant.now())
                    .build());
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to serialize outbox event " + eventType, ex);
        }
    }
}

