package com.example.demo.notification.dto;

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
public class NotificationRealtimeMessage {

    private String type;

    private Long unreadCount;

    private UUID notificationId;

    private NotificationResponse notification;
}

