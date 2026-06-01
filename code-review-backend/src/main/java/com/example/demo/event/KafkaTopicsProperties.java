package com.example.demo.event;

import org.springframework.boot.context.properties.ConfigurationProperties;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@ConfigurationProperties(prefix = "app.kafka.topics")
public class KafkaTopicsProperties {

    private String assignment = "assignment-events";
    private String submission = "submission-events";
    private String review = "review-events";
}

