package com.todoapp.interfaces.dto.todo;

import com.todoapp.infrastructure.jooq.enums.Priority;

import java.time.Instant;
import java.util.UUID;

public record TodoResponseDto(
    UUID id,
    UUID ownerId,
    String description,
    Boolean completed,
    Priority priority,
    Instant dueDate,
    Instant createdAt,
    Instant updatedAt
) {}
