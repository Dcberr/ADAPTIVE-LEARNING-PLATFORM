package com.example.demo.auth.service;

import org.springframework.stereotype.Service;

import com.example.demo.user.entity.Role;
import com.example.demo.user.entity.User;
import com.example.demo.user.repository.UserRepository;
import com.example.demo.user.service.UserService;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final UserService userService;

    public User findOrCreateOAuthUser(
            String email,
            String name,
            String picture
    ) {

        return userRepository.findByEmail(email)
        .orElseGet(() -> {

            String userCode =
                    userService.generateUserCode(Role.STUDENT);

            return userRepository.save(
                    User.builder()
                            .email(email)
                            .name(name)
                            .picture(picture)
                            .provider("google")
                            .role(Role.STUDENT)
                            .userCode(userCode)
                            .build()
            );
        });
    }

}
