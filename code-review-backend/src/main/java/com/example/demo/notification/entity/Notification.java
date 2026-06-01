package com.example.demo.notification.entity;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(
        name = "notifications",
        uniqueConstraints = @UniqueConstraint(
        name = "uk_notification_user_source_event",
                columnNames = {"user_id", "source_event_id"}
        )
)
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Notification {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(name = "user_id")
    private UUID userId;

    @Column(name = "source_event_id")
    private UUID sourceEventId;

    private String type;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String message;

    private String resourceType;

    @Column(name = "resource_id")
    private UUID resourceId;

    private boolean read;

    private Instant readAt;

    @Column(columnDefinition = "TEXT")
    private String metadataJson;

    private Instant createdAt;

    @PrePersist
    void prePersist() {
        if (createdAt == null) {
            createdAt = Instant.now();
        }
    }
}
