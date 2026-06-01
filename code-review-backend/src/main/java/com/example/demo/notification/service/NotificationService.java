package com.example.demo.notification.service;

import java.util.Collection;
import java.util.List;
import java.util.UUID;

import com.example.demo.notification.dto.NotificationResponse;
import com.example.demo.notification.dto.NotificationUnreadCountResponse;

public interface NotificationService {

    List<NotificationResponse> getNotifications(UUID userId);

    NotificationResponse markAsRead(UUID userId, UUID notificationId);

    NotificationUnreadCountResponse getUnreadCount(UUID userId);

    void createNotifications(Collection<UUID> userIds, UUID sourceEventId, String type, String title,
                             String message, String resourceType, UUID resourceId, Object metadata);
}

