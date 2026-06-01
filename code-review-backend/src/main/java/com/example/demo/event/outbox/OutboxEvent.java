package com.example.demo.event.outbox;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "outbox_events")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OutboxEvent {

    @Id
    private UUID id;

    private String topic;

    private String keyValue;

    private String eventType;

    private String aggregateType;

    private String aggregateId;

    @Column(columnDefinition = "TEXT")
    private String payload;

    @Enumerated(EnumType.STRING)
    private OutboxEventStatus status;

    private Integer attempts;

    private Instant createdAt;

    private Instant publishedAt;

    @Column(columnDefinition = "TEXT")
    private String lastError;

    @PrePersist
    void prePersist() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        if (status == null) {
            status = OutboxEventStatus.PENDING;
        }
        if (attempts == null) {
            attempts = 0;
        }
        if (createdAt == null) {
            createdAt = Instant.now();
        }
    }
}

