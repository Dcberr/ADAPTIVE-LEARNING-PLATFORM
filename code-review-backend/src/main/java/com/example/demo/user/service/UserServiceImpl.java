package com.example.demo.user.service;

import java.time.Year;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;

import com.example.demo.user.dto.UpdateUserRequest;
import com.example.demo.user.dto.UserResponse;
import com.example.demo.user.entity.Role;
import com.example.demo.user.entity.User;
import com.example.demo.user.entity.UserCodeSequence;
import com.example.demo.user.repository.UserCodeSequenceRepository;
import com.example.demo.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final UserCodeSequenceRepository userCodeSequenceRepository;

    @Override
    public UserResponse getCurrentUser(UUID userId) {

        User user = userRepository.findById(userId)
                .orElseThrow();

        return mapToResponse(user);
    }

    @Override
    public UserResponse getUserById(UUID userId) {

        User user = userRepository.findById(userId)
                .orElseThrow();

        return mapToResponse(user);
    }

    @Override
    public UserResponse updateUser(UUID userId, UpdateUserRequest request) {

        User user = userRepository.findById(userId)
                .orElseThrow();

        user.setName(request.getName());
        user.setPicture(request.getPicture());

        userRepository.save(user);

        return mapToResponse(user);
    }

    private UserResponse mapToResponse(User user) {

        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .picture(user.getPicture())
                .role(user.getRole().name())
                .build();
    }

    @Transactional
    public String generateUserCode(Role role) {

        int year = Year.now().getValue();

        UserCodeSequence seq =
                userCodeSequenceRepository.findByRoleAndYear(role.name(), year)
                        .orElseGet(() -> userCodeSequenceRepository.save(
                                UserCodeSequence.builder()
                                        .role(role.name())
                                        .year(year)
                                        .currentValue(0)
                                        .build()
                        ));

        int next = seq.getCurrentValue() + 1;
        seq.setCurrentValue(next);

        userCodeSequenceRepository.save(seq);

        return format(role, year, next);
    }

    private String format(Role role, int year, int number) {

        return String.format(
                "%s-%d-%05d",
                role.getPrefix(),
                year,
                number
        );
    }

    
}