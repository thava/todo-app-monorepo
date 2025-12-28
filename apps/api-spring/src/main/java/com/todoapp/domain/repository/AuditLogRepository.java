package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.tables.AuditLogs;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;

@Slf4j
@Repository
@RequiredArgsConstructor
public class AuditLogRepository {

    private final DSLContext dsl;
    private static final AuditLogs AUDIT_LOGS = AuditLogs.AUDIT_LOGS;

    public void createLog(UUID userId, String action, String metadata,
                          String ipAddress, String userAgent) {
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        dsl.insertInto(AUDIT_LOGS)
            .set(AUDIT_LOGS.USER_ID, userId)
            .set(AUDIT_LOGS.ACTION, action)
            .set(AUDIT_LOGS.IP_ADDRESS, ipAddress)
            .set(AUDIT_LOGS.USER_AGENT, userAgent)
            .set(AUDIT_LOGS.METADATA, metadata != null ? JSONB.valueOf(metadata) : null)
            .set(AUDIT_LOGS.CREATED_AT, now)
            .execute();

        log.debug("Created audit log: {} for user: {}", action, userId);
    }

    public List<AuditLog> findByUserId(UUID userId, int limit, int offset) {
        return dsl.selectFrom(AUDIT_LOGS)
            .where(AUDIT_LOGS.USER_ID.eq(userId))
            .orderBy(AUDIT_LOGS.CREATED_AT.desc())
            .limit(limit)
            .offset(offset)
            .fetch()
            .map(record -> new AuditLog(
                record.get(AUDIT_LOGS.ID),
                record.get(AUDIT_LOGS.USER_ID),
                record.get(AUDIT_LOGS.ACTION),
                record.get(AUDIT_LOGS.METADATA) != null ? record.get(AUDIT_LOGS.METADATA).data() : null,
                record.get(AUDIT_LOGS.IP_ADDRESS),
                record.get(AUDIT_LOGS.USER_AGENT),
                record.get(AUDIT_LOGS.CREATED_AT).toInstant()
            ));
    }

    public List<AuditLog> findAll(int limit, int offset) {
        return dsl.selectFrom(AUDIT_LOGS)
            .orderBy(AUDIT_LOGS.CREATED_AT.desc())
            .limit(limit)
            .offset(offset)
            .fetch()
            .map(record -> new AuditLog(
                record.get(AUDIT_LOGS.ID),
                record.get(AUDIT_LOGS.USER_ID),
                record.get(AUDIT_LOGS.ACTION),
                record.get(AUDIT_LOGS.METADATA) != null ? record.get(AUDIT_LOGS.METADATA).data() : null,
                record.get(AUDIT_LOGS.IP_ADDRESS),
                record.get(AUDIT_LOGS.USER_AGENT),
                record.get(AUDIT_LOGS.CREATED_AT).toInstant()
            ));
    }

    public record AuditLog(
        UUID id,
        UUID userId,
        String action,
        String metadata,
        String ipAddress,
        String userAgent,
        Instant createdAt
    ) {}
}
