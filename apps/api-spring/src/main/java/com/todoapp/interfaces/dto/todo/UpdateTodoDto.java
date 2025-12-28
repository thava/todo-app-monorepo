package com.todoapp.interfaces.dto.todo;

import com.todoapp.infrastructure.jooq.enums.Priority;
import jakarta.validation.constraints.Size;

import java.time.Instant;

public record UpdateTodoDto(
    @Size(min = 1, max = 5000, message = "Description must be between 1 and 5000 characters")
    String description,

    Priority priority,

    Boolean completed,

    Instant dueDate
) {}
