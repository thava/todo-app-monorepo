package com.todoapp.interfaces.dto.admin;

import java.time.Instant;
import java.util.UUID;

public record AuditLogResponseDto(
    UUID id,
    UUID userId,
    String action,
    String metadata,
    String ipAddress,
    String userAgent,
    Instant createdAt
) {}
