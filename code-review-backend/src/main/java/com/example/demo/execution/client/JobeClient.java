package com.example.demo.execution.client;

import java.util.UUID;

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
        String requestId = UUID.randomUUID().toString().substring(0, 8);
        String normalizedInput = normalizeInputForJobe(input);

        log.info(
                "[JOBE:{}] Starting run | language={} | stdin={} | stdinHex={} | normalizedStdin={} | normalizedStdinHex={} | source={}",
                requestId,
                language,
                quoteForLog(input),
                toHexForLog(input),
                quoteForLog(normalizedInput),
                toHexForLog(normalizedInput),
                quoteForLog(code)
        );

                
        String url = jobeBaseUrl + "/runs";

        Map<String, Object> runSpec = Map.of(
                "language_id", language,
                "sourcecode", code,
                "input", normalizedInput,
                "profiling", true
        );

        Map<String, Object> body = Map.of(
                "run_spec", runSpec
        );

        long startTime = System.currentTimeMillis(); 
        Map response =
                restTemplate.postForObject(url, body, Map.class);
        long runTime = System.currentTimeMillis() - startTime;
        log.info("[JOBE:{}] Finished run in {} ms | response={}", requestId, runTime, response);

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
                        runTime
                )
                        .build();
        }

        public ExecutionResult compile(String language, String code) {
                String requestId = UUID.randomUUID().toString().substring(0, 8);
                log.info(
                        "[JOBE:{}] Starting compile | language={} | source={}",
                        requestId,
                        language,
                        quoteForLog(code)
                );

                String url = jobeBaseUrl + "/runs";

                Map<String, Object> runSpec = Map.of(
                        "language_id", language,
                        "sourcecode", code,
                        "input", ""
                );

                Map<String, Object> body = Map.of(
                        "run_spec", runSpec
                );

                long startTime = System.currentTimeMillis();
                Map response =
                        restTemplate.postForObject(url, body, Map.class);
                long runTime = System.currentTimeMillis() - startTime;
                log.info("[JOBE:{}] Finished compile in {} ms | response={}", requestId, runTime, response);

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
                                runTime
                        )
                        .build();
        }

        private String quoteForLog(String value) {
                if (value == null) {
                        return "<null>";
                }

                String escaped = value
                        .replace("\\", "\\\\")
                        .replace("\r", "\\r")
                        .replace("\n", "\\n")
                        .replace("\t", "\\t");

                if (escaped.length() > 1200) {
                        return "\"" + escaped.substring(0, 1200) + "...(truncated)\"";
                }

                return "\"" + escaped + "\"";
        }

        private String toHexForLog(String value) {
                if (value == null) {
                        return "<null>";
                }

                StringBuilder builder = new StringBuilder();
                for (int i = 0; i < value.length(); i++) {
                        if (i > 0) {
                                builder.append(' ');
                        }
                        builder.append(String.format("%02X", (int) value.charAt(i)));
                }
                return builder.toString();
        }

        private String normalizeInputForJobe(String input) {
                if (input == null || input.isEmpty()) {
                        return "";
                }

                if (input.endsWith("\n")) {
                        return input;
                }

                return input + "\n";
        }
}
