package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.tables.AuditLogs;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.springframework.stereotype.Repository;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Repository
@RequiredArgsConstructor
public class AuditLogRepository {

    private final DSLContext dsl;
    private static final AuditLogs AUDIT_LOGS = AuditLogs.AUDIT_LOGS;

    public void createLog(UUID userId, String action, String entityType, UUID entityId,
                          String ipAddress, String userAgent, Map<String, Object> metadata) {
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        String metadataJson = "{" +
            (metadata != null && !metadata.isEmpty() ?
                metadata.entrySet().stream()
                    .map(e -> "\"" + e.getKey() + "\":\"" + e.getValue() + "\"")
                    .reduce((a, b) -> a + "," + b)
                    .orElse("") : "") +
            "}";

        dsl.insertInto(AUDIT_LOGS)
            .set(AUDIT_LOGS.USER_ID, userId)
            .set(AUDIT_LOGS.ACTION, action)
            .set(AUDIT_LOGS.ENTITY_TYPE, entityType)
            .set(AUDIT_LOGS.ENTITY_ID, entityId)
            .set(AUDIT_LOGS.IP_ADDRESS, ipAddress)
            .set(AUDIT_LOGS.USER_AGENT, userAgent)
            .set(AUDIT_LOGS.METADATA, JSONB.valueOf(metadataJson))
            .set(AUDIT_LOGS.CREATED_AT, now)
            .execute();

        log.debug("Created audit log: {} for user: {}", action, userId);
    }
}
