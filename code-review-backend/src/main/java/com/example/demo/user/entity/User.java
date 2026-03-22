package com.example.demo.user.entity;

import jakarta.annotation.Nullable;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue
    private java.util.UUID id;

    private String userCode;

    private String name;

    @Column(unique = true)
    private String email;

    private String picture;

    @Enumerated(EnumType.STRING)
    private Role role;

    private String provider;

    // private String phoneNumber;

    // private String enrollment;

    // private String address;

    // private String bio;

    @Nullable
    private float gpa;

}
