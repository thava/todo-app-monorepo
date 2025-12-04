package com.todoapp.interfaces.dto.todo;

import com.todoapp.domain.model.Priority;

import java.time.Instant;
import java.util.UUID;

public record TodoResponseDto(
    UUID id,
    UUID ownerId,
    String title,
    String description,
    Priority priority,
    boolean completed,
    Instant dueDate,
    Instant createdAt,
    Instant updatedAt
) {}
