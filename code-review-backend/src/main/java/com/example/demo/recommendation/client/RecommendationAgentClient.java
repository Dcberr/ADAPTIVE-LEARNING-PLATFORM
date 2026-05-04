package com.example.demo.recommendation.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.example.demo.common.exception.AppException;
import com.example.demo.common.exception.ErrorCode;
import com.example.demo.recommendation.dto.RecommendationAgentRequest;
import com.example.demo.recommendation.dto.RecommendationResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class RecommendationAgentClient {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${recommend.url}")
    private String recommendUrl;

    public RecommendationResponse getRecommendation(RecommendationAgentRequest requestBody) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<RecommendationAgentRequest> request = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<RecommendationResponse> response = restTemplate.postForEntity(
                    recommendUrl,
                    request,
                    RecommendationResponse.class
            );

            RecommendationResponse body = response.getBody();
            if (body == null) {
                throw new AppException(ErrorCode.RECOMMENDATION_SERVICE_ERROR);
            }

            return body;
        } catch (RestClientException ex) {
            log.error("Failed to call recommendation service at {}", recommendUrl, ex);
            throw new AppException(ErrorCode.RECOMMENDATION_SERVICE_ERROR);
        }
    }
}
