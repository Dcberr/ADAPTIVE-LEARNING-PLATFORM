package com.example.demo.auth.service;

import java.util.Collections;

import org.springframework.stereotype.Service;

import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.util.Value;

import lombok.extern.slf4j.Slf4j;

@Service
@Slf4j
public class GoogleTokenService {

    private final GoogleIdTokenVerifier verifier;

    @Value("${google.client-id}")
    private String CLIENT_ID;

    public GoogleTokenService() {

        verifier = new GoogleIdTokenVerifier.Builder(
                new NetHttpTransport(),
                new GsonFactory())
                .setAudience(Collections.singletonList(CLIENT_ID))
                .build();
    }

    public GoogleIdToken.Payload verify(String idTokenString) {

        try {
            log.info("Google token: {}", idTokenString);

            GoogleIdToken idToken = verifier.verify(idTokenString);

            if (idToken == null) {
                throw new RuntimeException("Invalid Google token");
            }

            return idToken.getPayload();

        } catch (Exception e) {
            log.error("Google token verification failed", e);
            throw new RuntimeException("Google token verification failed", e);
        }
    }

}
