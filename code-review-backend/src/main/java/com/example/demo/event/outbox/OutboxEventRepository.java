package com.example.demo.event.outbox;

import java.util.Collection;
import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {

    List<OutboxEvent> findTop50ByStatusInOrderByCreatedAtAsc(Collection<OutboxEventStatus> statuses);
}

