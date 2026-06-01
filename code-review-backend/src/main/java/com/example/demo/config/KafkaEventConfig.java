package com.example.demo.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.scheduling.annotation.EnableScheduling;

import com.example.demo.event.KafkaTopicsProperties;

@Configuration
@EnableKafka
@EnableScheduling
@EnableConfigurationProperties(KafkaTopicsProperties.class)
public class KafkaEventConfig {
}

