package com.example.demo.assignment.mapper;

import org.mapstruct.BeanMapping;
import org.mapstruct.Mapper;
import org.mapstruct.MappingTarget;
import org.mapstruct.NullValuePropertyMappingStrategy;

import com.example.demo.assignment.dto.UpdateAssignmentRequest;
import com.example.demo.assignment.entity.Assignment;

@Mapper(componentModel = "spring")
public interface AssignmentMapper {

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    void updateAssignmentFromDto(UpdateAssignmentRequest dto, @MappingTarget Assignment entity);
}
