package com.example.demo.event.model;

import java.time.Instant;
import java.util.UUID;

import com.fasterxml.jackson.databind.JsonNode;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventEnvelope {

    private UUID eventId;

    private String eventType;

    private String aggregateType;

    private String aggregateId;

    private Instant occurredAt;

    private JsonNode payload;
}

