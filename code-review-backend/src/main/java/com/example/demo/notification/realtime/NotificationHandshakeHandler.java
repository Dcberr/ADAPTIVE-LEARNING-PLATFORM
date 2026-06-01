package com.example.demo.notification.realtime;

import java.security.Principal;
import java.util.Map;
import java.util.UUID;

import org.springframework.http.server.ServerHttpRequest;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.support.DefaultHandshakeHandler;

public class NotificationHandshakeHandler extends DefaultHandshakeHandler {

    @Override
    protected Principal determineUser(ServerHttpRequest request, WebSocketHandler wsHandler,
                                      Map<String, Object> attributes) {
        Object userId = attributes.get(NotificationHandshakeInterceptor.USER_ID_ATTRIBUTE);
        if (userId instanceof UUID uuid) {
            return new NotificationPrincipal(uuid);
        }
        return null;
    }
}

