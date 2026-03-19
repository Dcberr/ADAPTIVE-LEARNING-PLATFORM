package com.example.demo.auth.service;

import org.springframework.stereotype.Service;

import com.example.demo.user.entity.User;
import com.example.demo.user.entity.User.UserRole;
import com.example.demo.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;

    public User findOrCreateOAuthUser(
            String email,
            String name,
            String picture
    ) {

        return userRepository.findByEmail(email)
                .orElseGet(() ->
                        userRepository.save(
                                User.builder()
                                        .email(email)
                                        .name(name)
                                        .picture(picture)
                                        .provider("google")
                                        .role(UserRole.STUDENT)
                                        .build()
                        )
                );
    }

}
