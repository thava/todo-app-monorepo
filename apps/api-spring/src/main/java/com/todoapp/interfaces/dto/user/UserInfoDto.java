package com.todoapp.interfaces.dto.user;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.todoapp.infrastructure.jooq.enums.Role;

import java.time.Instant;
import java.util.UUID;

public record UserInfoDto(
    UUID id,
    String email,
    String fullName,
    Role role,
    Instant emailVerifiedAt,
    String localUsername,
    String googleEmail,
    String msEmail,
    Instant createdAt,
    Instant updatedAt
) {
    @JsonProperty("emailVerified")
    public boolean emailVerified() {
        return emailVerifiedAt != null;
    }
}
