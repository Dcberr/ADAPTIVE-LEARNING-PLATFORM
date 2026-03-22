package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.example.demo.auth.security.CustomOAuth2AuthorizationRequestRepository;
import com.example.demo.auth.security.JwtAuthenticationFilter;
import com.example.demo.auth.security.OAuth2SuccessHandler;

import lombok.RequiredArgsConstructor;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final OAuth2SuccessHandler successHandler;
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final CustomOAuth2AuthorizationRequestRepository customRepo;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

        http
            .cors(Customizer.withDefaults())
            .csrf(csrf -> csrf.disable())

            .authorizeHttpRequests(auth -> auth
                    .requestMatchers(
                            "/",
                            "/error",
                            "/oauth2/**",
                            "/login/**"
                    ).permitAll()
                    .anyRequest().authenticated()
            )

            .oauth2Login(oauth -> oauth
                    .authorizationEndpoint(endpoint ->
                        endpoint.authorizationRequestRepository(customRepo)
                    )
                    .successHandler(successHandler)
            )

            .addFilterBefore(
                    jwtAuthenticationFilter,
                    UsernamePasswordAuthenticationFilter.class
            );

        return http.build();
    }
}