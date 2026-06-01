package com.example.demo.notification.realtime;

import java.io.IOException;
import java.security.Principal;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import com.example.demo.notification.dto.NotificationRealtimeMessage;
import com.example.demo.notification.repository.NotificationRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class NotificationWebSocketHandler extends TextWebSocketHandler {

    private final ObjectMapper objectMapper;
    private final NotificationRepository notificationRepository;
    private final Map<UUID, Set<WebSocketSession>> sessionsByUser = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        UUID userId = getUserId(session.getPrincipal());
        if (userId == null) {
            closeSilently(session, CloseStatus.NOT_ACCEPTABLE.withReason("Unauthorized"));
            return;
        }

        sessionsByUser
                .computeIfAbsent(userId, ignored -> ConcurrentHashMap.newKeySet())
                .add(session);

        sendToUser(userId, NotificationRealtimeMessage.builder()
                .type("connected")
                .unreadCount(notificationRepository.countByUserIdAndReadFalse(userId))
                .build());
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        UUID userId = getUserId(session.getPrincipal());
        if (userId == null) {
            return;
        }

        Set<WebSocketSession> userSessions = sessionsByUser.get(userId);
        if (userSessions == null) {
            return;
        }

        userSessions.remove(session);
        if (userSessions.isEmpty()) {
            sessionsByUser.remove(userId);
        }
    }

    public void sendToUser(UUID userId, NotificationRealtimeMessage message) {
        Set<WebSocketSession> userSessions = sessionsByUser.get(userId);
        if (userSessions == null || userSessions.isEmpty()) {
            return;
        }

        String payload;
        try {
            payload = objectMapper.writeValueAsString(message);
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to serialize realtime notification payload", ex);
        }

        userSessions.removeIf(session -> !session.isOpen());
        for (WebSocketSession session : userSessions) {
            try {
                session.sendMessage(new TextMessage(payload));
            } catch (IOException ex) {
                log.warn("Failed to send websocket notification to user={}", userId, ex);
            }
        }
    }

    private UUID getUserId(Principal principal) {
        if (principal == null || principal.getName() == null) {
            return null;
        }
        try {
            return UUID.fromString(principal.getName());
        } catch (IllegalArgumentException ex) {
            return null;
        }
    }

    private void closeSilently(WebSocketSession session, CloseStatus status) {
        try {
            session.close(status);
        } catch (IOException ex) {
            log.debug("Failed to close unauthorized websocket session", ex);
        }
    }
}

