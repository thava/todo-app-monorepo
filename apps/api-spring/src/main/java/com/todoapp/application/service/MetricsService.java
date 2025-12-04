package com.todoapp.application.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

import static com.todoapp.infrastructure.jooq.tables.Users.USERS;
import static com.todoapp.infrastructure.jooq.tables.Todos.TODOS;
import static com.todoapp.infrastructure.jooq.tables.AuditLogs.AUDIT_LOGS;

@Slf4j
@Service
@RequiredArgsConstructor
public class MetricsService {

    private final DSLContext dsl;

    public Map<String, Object> getSystemMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        metrics.put("totalUsers", getTotalUsers());
        metrics.put("totalTodos", getTotalTodos());
        metrics.put("completedTodos", getCompletedTodos());
        metrics.put("totalAuditLogs", getTotalAuditLogs());
        metrics.put("usersByRole", getUsersByRole());
        metrics.put("todosByPriority", getTodosByPriority());
        
        return metrics;
    }

    private long getTotalUsers() {
        return dsl.selectCount()
            .from(USERS)
            .fetchOne(0, Long.class);
    }

    private long getTotalTodos() {
        return dsl.selectCount()
            .from(TODOS)
            .fetchOne(0, Long.class);
    }

    private long getCompletedTodos() {
        return dsl.selectCount()
            .from(TODOS)
            .where(TODOS.COMPLETED.isTrue())
            .fetchOne(0, Long.class);
    }

    private long getTotalAuditLogs() {
        return dsl.selectCount()
            .from(AUDIT_LOGS)
            .fetchOne(0, Long.class);
    }

    private Map<String, Long> getUsersByRole() {
        return dsl.select(USERS.ROLE, org.jooq.impl.DSL.count())
            .from(USERS)
            .groupBy(USERS.ROLE)
            .fetchMap(USERS.ROLE, org.jooq.impl.DSL.count());
    }

    private Map<String, Long> getTodosByPriority() {
        return dsl.select(TODOS.PRIORITY, org.jooq.impl.DSL.count())
            .from(TODOS)
            .groupBy(TODOS.PRIORITY)
            .fetchMap(TODOS.PRIORITY, org.jooq.impl.DSL.count());
    }
}
