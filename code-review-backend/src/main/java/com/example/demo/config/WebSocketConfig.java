package com.example.demo.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

import com.example.demo.notification.realtime.NotificationHandshakeHandler;
import com.example.demo.notification.realtime.NotificationHandshakeInterceptor;
import com.example.demo.notification.realtime.NotificationWebSocketHandler;

import lombok.RequiredArgsConstructor;

@Configuration
@EnableWebSocket
@RequiredArgsConstructor
public class WebSocketConfig implements WebSocketConfigurer {

    private final NotificationWebSocketHandler notificationWebSocketHandler;
    private final NotificationHandshakeInterceptor notificationHandshakeInterceptor;

    @Value("${application.url}")
    private String applicationUrl;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(notificationWebSocketHandler, "/ws/notifications")
                .addInterceptors(notificationHandshakeInterceptor)
                .setHandshakeHandler(new NotificationHandshakeHandler())
                .setAllowedOrigins(
                        applicationUrl,
                        "http://localhost:3000",
                        "https://localhost:3000"
                );
    }
}
