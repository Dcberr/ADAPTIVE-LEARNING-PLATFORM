package com.example.demo.notification.realtime;

import java.util.UUID;

import org.springframework.stereotype.Component;

import com.example.demo.notification.dto.NotificationRealtimeMessage;
import com.example.demo.notification.dto.NotificationResponse;
import com.example.demo.notification.repository.NotificationRepository;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class NotificationRealtimeGateway {

    private final NotificationRepository notificationRepository;
    private final NotificationWebSocketHandler notificationWebSocketHandler;

    public void sendCreated(UUID userId, NotificationResponse notification) {
        notificationWebSocketHandler.sendToUser(userId, NotificationRealtimeMessage.builder()
                .type("notification.created")
                .notification(notification)
                .notificationId(notification.getId())
                .unreadCount(notificationRepository.countByUserIdAndReadFalse(userId))
                .build());
    }

    public void sendMarkedRead(UUID userId, UUID notificationId) {
        notificationWebSocketHandler.sendToUser(userId, NotificationRealtimeMessage.builder()
                .type("notification.read")
                .notificationId(notificationId)
                .unreadCount(notificationRepository.countByUserIdAndReadFalse(userId))
                .build());
    }
}

