package com.todoapp.interfaces.dto.admin;

import java.util.UUID;

public record MergeAccountsResponseDto(
    String message,
    UUID destinationUserId,
    MergedIdentitiesDto mergedIdentities
) {}
