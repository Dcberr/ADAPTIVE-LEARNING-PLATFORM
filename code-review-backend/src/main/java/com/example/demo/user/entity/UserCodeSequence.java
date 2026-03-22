package com.example.demo.user.entity;

import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "user_code_sequences")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserCodeSequence {

    @Id
    @GeneratedValue
    private UUID id;

    private String role;

    private Integer year;

    private Integer currentValue;
}
