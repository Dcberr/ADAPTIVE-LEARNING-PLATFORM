package com.example.demo.notification.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.common.response.ApiResponse;
import com.example.demo.notification.dto.NotificationResponse;
import com.example.demo.notification.dto.NotificationUnreadCountResponse;
import com.example.demo.notification.service.NotificationService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
@Tag(name = "Notification", description = "APIs for event-driven notifications")
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping("/me")
    @Operation(summary = "Get my notifications")
    public ApiResponse<List<NotificationResponse>> getMyNotifications(Authentication authentication) {
        UUID userId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(notificationService.getNotifications(userId));
    }

    @GetMapping("/me/unread-count")
    @Operation(summary = "Get my unread notification count")
    public ApiResponse<NotificationUnreadCountResponse> getUnreadCount(Authentication authentication) {
        UUID userId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(notificationService.getUnreadCount(userId));
    }

    @PostMapping("/{notificationId}/read")
    @Operation(summary = "Mark one notification as read")
    public ApiResponse<NotificationResponse> markAsRead(
            Authentication authentication,
            @PathVariable UUID notificationId
    ) {
        UUID userId = (UUID) authentication.getPrincipal();
        return ApiResponse.success(notificationService.markAsRead(userId, notificationId));
    }
}

