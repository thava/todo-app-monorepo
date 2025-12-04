package com.todoapp.interfaces.dto.auth;

import jakarta.validation.constraints.NotBlank;

public record RefreshTokenDto(
    @NotBlank(message = "Refresh token is required")
    String refreshToken
) {}
