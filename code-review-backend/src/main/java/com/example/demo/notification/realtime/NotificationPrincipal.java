package com.example.demo.notification.realtime;

import java.security.Principal;
import java.util.UUID;

public record NotificationPrincipal(UUID userId) implements Principal {

    @Override
    public String getName() {
        return userId.toString();
    }
}

