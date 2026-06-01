package com.example.demo.notification.repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.notification.entity.Notification;

public interface NotificationRepository extends JpaRepository<Notification, UUID> {

    List<Notification> findByUserIdOrderByCreatedAtDesc(UUID userId);

    long countByUserIdAndReadFalse(UUID userId);

    boolean existsByUserIdAndSourceEventId(UUID userId, UUID sourceEventId);

    Optional<Notification> findByIdAndUserId(UUID id, UUID userId);
}

