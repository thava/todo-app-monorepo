package com.todoapp.interfaces.dto.admin;

import jakarta.validation.constraints.NotNull;

import java.util.UUID;

public record MergeAccountsDto(
    @NotNull(message = "Source user ID is required")
    UUID sourceUserId,

    @NotNull(message = "Destination user ID is required")
    UUID destinationUserId
) {}
