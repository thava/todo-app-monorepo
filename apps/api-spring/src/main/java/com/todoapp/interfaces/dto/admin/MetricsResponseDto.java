package com.todoapp.interfaces.dto.admin;

import java.util.Map;

public record MetricsResponseDto(
    long totalUsers,
    long totalTodos,
    long completedTodos,
    long totalAuditLogs,
    Map<String, Long> usersByRole,
    Map<String, Long> todosByPriority
) {}
