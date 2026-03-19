package com.example.demo.execution.client;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.example.demo.execution.dto.ExecutionResult;

import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class JobeClient {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${jobe.base-url}")
    private String jobeBaseUrl;

    public ExecutionResult runCode(
                String language,
                String code,
                String input
        ) {

        log.info(input);
        log.info(code);

        log.info("stdin: [{}]", input);

                
        String url = jobeBaseUrl + "/runs";

        Map<String, Object> runSpec = Map.of(
                "language_id", language,
                "sourcecode", code,
                "input", input,
                "profiling", true
        );

        Map<String, Object> body = Map.of(
                "run_spec", runSpec
        );

        Map response =
                restTemplate.postForObject(url, body, Map.class);

        log.info("JOBE response: {}", response);

        return ExecutionResult.builder()
                .stdout((String) response.get("stdout"))
                .stderr((String) response.get("cmpinfo") == null || ((String) response.get("cmpinfo")).isEmpty()        
                        ? (String) response.get("stderr")
                        : (String) response.get("cmpinfo"))
                .exitCode(
                        response.get("outcome") == null
                                ? 0
                                : ((Number) response.get("outcome")).intValue()
                )
                .runtime(
                        response.get("time") == null
                                ? 0
                                : ((Number) response.get("time")).longValue()
                )
                .build();
        }

        public ExecutionResult compile(String language, String code) {

                String url = jobeBaseUrl + "/runs";

                Map<String, Object> runSpec = Map.of(
                        "language_id", language,
                        "sourcecode", code,
                        "input", ""
                );

                Map<String, Object> body = Map.of(
                        "run_spec", runSpec
                );
                Map response =
                        restTemplate.postForObject(url, body, Map.class);

                return ExecutionResult.builder()
                        .stdout((String) response.get("stdout"))
                        .stderr((String) response.get("cmpinfo") == null || ((String) response.get("cmpinfo")).isEmpty()        
                                ? (String) response.get("stderr")
                                : (String) response.get("cmpinfo"))
                        .exitCode(
                                response.get("outcome") == null
                                        ? 0
                                        : ((Number) response.get("outcome")).intValue()
                        )
                        .runtime(
                                response.get("time") == null
                                        ? 0
                                        : ((Number) response.get("time")).longValue()
                        )
                        .build();
        }
}