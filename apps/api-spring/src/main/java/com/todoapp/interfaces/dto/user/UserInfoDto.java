package com.todoapp.interfaces.dto.user;

import com.todoapp.domain.model.Role;

import java.time.Instant;
import java.util.UUID;

public record UserInfoDto(
    UUID id,
    String email,
    String fullName,
    Role role,
    Instant emailVerifiedAt,
    Instant createdAt,
    Instant updatedAt
) {}
