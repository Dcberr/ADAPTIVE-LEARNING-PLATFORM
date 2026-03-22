package com.example.demo.user.repository;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.user.entity.UserCodeSequence;

@Repository
public interface UserCodeSequenceRepository
        extends JpaRepository<UserCodeSequence, UUID> {

    Optional<UserCodeSequence> findByRoleAndYear(String role, Integer year);

}
