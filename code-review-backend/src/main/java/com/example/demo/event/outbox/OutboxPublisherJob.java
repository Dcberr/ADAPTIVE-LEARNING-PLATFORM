package com.example.demo.event.outbox;

import java.time.Instant;
import java.util.List;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class OutboxPublisherJob {

    private final OutboxEventRepository outboxEventRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelayString = "${app.kafka.outbox.publish-delay-ms:3000}")
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> events = outboxEventRepository.findTop50ByStatusInOrderByCreatedAtAsc(
                List.of(OutboxEventStatus.PENDING, OutboxEventStatus.FAILED)
        );

        for (OutboxEvent event : events) {
            try {
                kafkaTemplate.send(event.getTopic(), event.getKeyValue(), event.getPayload()).get();
                event.setStatus(OutboxEventStatus.PUBLISHED);
                event.setPublishedAt(Instant.now());
                event.setLastError(null);
                event.setAttempts(event.getAttempts() + 1);
            } catch (Exception ex) {
                event.setStatus(OutboxEventStatus.FAILED);
                event.setAttempts(event.getAttempts() + 1);
                event.setLastError(truncate(ex.getMessage()));
                log.warn("Failed to publish outbox event id={} type={}", event.getId(), event.getEventType(), ex);
            }
        }
    }

    private String truncate(String message) {
        if (message == null || message.length() <= 1000) {
            return message;
        }
        return message.substring(0, 1000);
    }
}

