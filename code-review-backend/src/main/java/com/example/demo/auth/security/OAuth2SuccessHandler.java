package com.example.demo.auth.security;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import com.example.demo.auth.service.AuthService;
import com.example.demo.user.entity.User;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final AuthService authService;
    private final JwtProvider jwtProvider;

    @Value("${server.application.url}")
    private String applicationUrl;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication
    ) throws IOException {

        OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();

        String email = oauthUser.getAttribute("email");
        String name = oauthUser.getAttribute("name");
        String picture = oauthUser.getAttribute("picture");
        String role = (String) request.getSession().getAttribute("OAUTH2_ROLE");
        log.info("OAuth2 login success: email={}, name={}, picture={}, role={}", email, name, picture, role);

        User user = "instructor".equals(role)
                ? authService.findOrCreateOAuthInstructorUser(email, name, picture)
                : authService.findOrCreateOAuthStudentUser(email, name, picture);

        String token = jwtProvider.generateToken(user);

        Cookie cookie = new Cookie("access_token", token);
        cookie.setHttpOnly(true);
        cookie.setSecure(false); // true when use HTTPS
        cookie.setPath("/");
        cookie.setMaxAge(86400);

        response.addCookie(cookie);

        getRedirectStrategy().sendRedirect(
                request,
                response,
                applicationUrl + "/oauth-success"
        );
    }
}
