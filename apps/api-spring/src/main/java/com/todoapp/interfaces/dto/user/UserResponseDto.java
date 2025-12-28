package com.todoapp.interfaces.dto.user;

import com.todoapp.infrastructure.jooq.enums.Role;

import java.time.Instant;
import java.util.UUID;

public record UserResponseDto(
    UUID id,
    String email,
    String fullName,
    Role role,
    Instant emailVerifiedAt,
    Instant createdAt,
    Instant updatedAt
) {}
