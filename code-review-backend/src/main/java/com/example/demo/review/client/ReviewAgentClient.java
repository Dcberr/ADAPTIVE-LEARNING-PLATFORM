package com.example.demo.review.client;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.example.demo.review.dto.ReviewResponse;

import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class ReviewAgentClient {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${review.url}")
    private String reviewUrl;

    public ReviewResponse reviewCode(
            Map<String, Object> body
    ) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request =
                new HttpEntity<>(body, headers);

        log.info("Review request: {}", request);

        ResponseEntity<ReviewResponse> response =
                restTemplate.postForEntity(
                        reviewUrl,
                        request,
                        ReviewResponse.class
                );

        log.info("Review response: {}", response.getBody());

        return response.getBody();
    }
}