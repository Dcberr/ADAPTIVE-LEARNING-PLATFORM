package com.example.demo.classmanagement.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.classmanagement.entity.Class;

@Repository
public interface ClassRepository extends JpaRepository<Class, UUID> {

    List<Class> findByInstructorId(UUID instructorId);

}