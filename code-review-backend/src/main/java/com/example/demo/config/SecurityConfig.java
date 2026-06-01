package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.example.demo.auth.security.CustomOAuth2AuthorizationRequestRepository;
import com.example.demo.auth.security.JwtAuthenticationFilter;
import com.example.demo.auth.security.OAuth2SuccessHandler;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import lombok.RequiredArgsConstructor;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private static final String[] LECTURER_ROLES = {"INSTRUCTOR", "ADMIN"};
    private static final String[] LMS_ROLES = {"INSTRUCTOR", "STUDENT", "ADMIN"};

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
                            "/login/**",
                            "/ws/**",
                            "/swagger-ui/**",
                            "/v3/api-docs/**",
                            "/v3/api-docs.yaml/**"
                    ).permitAll()
                    .requestMatchers(HttpMethod.POST, "/classes").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/classes/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/classes/*/students/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/classes/*/students/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/classes/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/classes/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/topics/**").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/topics/**").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/topics/**").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/topics/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/documents").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/documents/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/documents/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/documents/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/assignments").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/assignments/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/assignments/topic/*/*/problems/leetcode").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/assignments/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/assignments/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/problems").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/problems/manual").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/problems/leetcode/batch").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/problems/leetcode/batch").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/problems/library/manual").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/problems/library/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.DELETE, "/problems/library/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/problems/source/library").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/problems/templates").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/problems/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/testcases").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.GET, "/testcases/problem/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.GET, "/testcases/assignment/*").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.POST, "/reviews/submission/*").hasAnyRole(LMS_ROLES)
                    .requestMatchers(HttpMethod.GET, "/reviews/problem/*/user/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers("/reviews/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.GET, "/submissions/assignment/*/me").hasAnyRole(LMS_ROLES)
                    .requestMatchers(HttpMethod.GET, "/submissions/problem/*/me").hasAnyRole(LMS_ROLES)
                    .requestMatchers(HttpMethod.GET, "/submissions/assignment/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.GET, "/submissions/assignment/*/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.GET, "/submissions/problem/*/*").hasAnyRole(LECTURER_ROLES)
                    .requestMatchers(HttpMethod.POST, "/submissions").hasAnyRole(LMS_ROLES)
                    .requestMatchers(HttpMethod.GET, "/submissions/**").hasAnyRole(LMS_ROLES)

                    .requestMatchers(HttpMethod.GET, "/users/me").hasAnyRole(LMS_ROLES)
                    .requestMatchers(HttpMethod.PUT, "/users/me").hasAnyRole(LMS_ROLES)
                    .requestMatchers("/users/**").hasAnyRole(LECTURER_ROLES)

                    .requestMatchers("/recommendations/**").hasAnyRole(LMS_ROLES)
                    .requestMatchers("/notifications/**").hasAnyRole(LMS_ROLES)
                    .requestMatchers("/execution/**").hasAnyRole(LMS_ROLES)
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

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .addSecurityItem(new SecurityRequirement().addList("bearerAuth"))
                .components(new Components()
                        .addSecuritySchemes("bearerAuth",
                                new SecurityScheme()
                                        .name("Authorization")
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                        )
                )
                .info(new Info().title("LMS API").version("1.0"));
    }
}
