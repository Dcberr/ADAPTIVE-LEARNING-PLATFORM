package com.example.demo.problem.client;

import java.net.URI;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import com.example.demo.problem.dto.LeetCodeProblemPageResponse;

import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
public class LeetCodeClient {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${leetcode.api-url}")
    private String leetCodeApiUrl;

    public LeetCodeProblemPageResponse getProblems(int page, int limit) {
        String primaryUrl = buildUrl(leetCodeApiUrl, page, limit);

        try {
            return restTemplate.getForObject(primaryUrl, LeetCodeProblemPageResponse.class);
        } catch (ResourceAccessException ex) {
            String fallbackBaseUrl = resolveDockerFallbackBaseUrl(leetCodeApiUrl);
            if (fallbackBaseUrl == null) {
                throw ex;
            }

            String fallbackUrl = buildUrl(fallbackBaseUrl, page, limit);
            log.warn("Failed to call LeetCode API via {}. Retrying with {}", primaryUrl, fallbackUrl);
            return restTemplate.getForObject(fallbackUrl, LeetCodeProblemPageResponse.class);
        }
    }

    private String buildUrl(String baseUrl, int page, int limit) {
        return UriComponentsBuilder
                .fromHttpUrl(baseUrl)
                .queryParam("page", page)
                .queryParam("limit", limit)
                .toUriString();
    }

    private String resolveDockerFallbackBaseUrl(String baseUrl) {
        URI uri = URI.create(baseUrl);
        String host = uri.getHost();

        if (host == null || (!"localhost".equals(host) && !"127.0.0.1".equals(host))) {
            return null;
        }

        return UriComponentsBuilder
                .newInstance()
                .scheme(uri.getScheme())
                .host("leetcode-crawler")
                .port(uri.getPort())
                .path(uri.getPath())
                .build()
                .toUriString();
    }
}
