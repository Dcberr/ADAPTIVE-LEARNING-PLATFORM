package com.example.demo.notification.service;

import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.notification.dto.NotificationResponse;
import com.example.demo.notification.dto.NotificationUnreadCountResponse;
import com.example.demo.notification.entity.Notification;
import com.example.demo.notification.repository.NotificationRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class NotificationServiceImpl implements NotificationService {

    private final NotificationRepository notificationRepository;
    private final ObjectMapper objectMapper;

    @Override
    public List<NotificationResponse> getNotifications(UUID userId) {
        return notificationRepository.findByUserIdOrderByCreatedAtDesc(userId).stream()
                .map(this::toResponse)
                .toList();
    }

    @Override
    @Transactional
    public NotificationResponse markAsRead(UUID userId, UUID notificationId) {
        Notification notification = notificationRepository.findByIdAndUserId(notificationId, userId)
                .orElseThrow(() -> new AppException(ErrorCode.VALIDATION_ERROR));

        if (!notification.isRead()) {
            notification.setRead(true);
            notification.setReadAt(Instant.now());
        }

        return toResponse(notification);
    }

    @Override
    public NotificationUnreadCountResponse getUnreadCount(UUID userId) {
        return NotificationUnreadCountResponse.builder()
                .unreadCount(notificationRepository.countByUserIdAndReadFalse(userId))
                .build();
    }

    @Override
    @Transactional
    public void createNotifications(Collection<UUID> userIds, UUID sourceEventId, String type, String title,
                                    String message, String resourceType, UUID resourceId, Object metadata) {
        if (userIds == null || userIds.isEmpty()) {
            return;
        }

        String metadataJson = serializeMetadata(metadata);
        List<Notification> notifications = userIds.stream()
                .distinct()
                .filter(userId -> !notificationRepository.existsByUserIdAndSourceEventId(userId, sourceEventId))
                .map(userId -> Notification.builder()
                        .userId(userId)
                        .sourceEventId(sourceEventId)
                        .type(type)
                        .title(title)
                        .message(message)
                        .resourceType(resourceType)
                        .resourceId(resourceId)
                        .read(false)
                        .metadataJson(metadataJson)
                        .createdAt(Instant.now())
                        .build())
                .toList();

        if (!notifications.isEmpty()) {
            notificationRepository.saveAll(notifications);
        }
    }

    private String serializeMetadata(Object metadata) {
        if (metadata == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(metadata);
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to serialize notification metadata", ex);
        }
    }

    private NotificationResponse toResponse(Notification notification) {
        return NotificationResponse.builder()
                .id(notification.getId())
                .type(notification.getType())
                .title(notification.getTitle())
                .message(notification.getMessage())
                .resourceType(notification.getResourceType())
                .resourceId(notification.getResourceId())
                .read(notification.isRead())
                .readAt(notification.getReadAt())
                .createdAt(notification.getCreatedAt())
                .build();
    }
}

