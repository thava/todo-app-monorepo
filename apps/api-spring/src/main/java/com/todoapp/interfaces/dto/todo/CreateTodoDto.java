package com.todoapp.interfaces.dto.todo;

import com.todoapp.domain.model.Priority;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.Instant;

public record CreateTodoDto(
    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 200, message = "Title must be between 1 and 200 characters")
    String title,
    
    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    String description,
    
    Priority priority,
    
    Instant dueDate
) {}
