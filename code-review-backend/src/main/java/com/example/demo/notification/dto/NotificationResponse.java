package com.example.demo.notification.dto;

import java.time.Instant;
import java.util.UUID;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationResponse {

    private UUID id;

    private String type;

    private String title;

    private String message;

    private String resourceType;

    private UUID resourceId;

    private boolean read;

    private Instant readAt;

    private Instant createdAt;
}

