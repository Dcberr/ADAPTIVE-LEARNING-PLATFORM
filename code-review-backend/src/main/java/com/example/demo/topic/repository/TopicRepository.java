package com.example.demo.topic.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.demo.topic.entity.Topic;

@Repository
public interface TopicRepository extends JpaRepository<Topic, UUID> {

    List<Topic> findByClassIdAndDeletedAtIsNull(UUID classId);

    java.util.Optional<Topic> findByIdAndDeletedAtIsNull(UUID id);

}
