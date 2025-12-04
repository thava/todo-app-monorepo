package com.todoapp.application.service;

import com.todoapp.domain.repository.AuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    @Async
    @Transactional
    public void logAction(UUID userId, String action, String metadata, 
                         String ipAddress, String userAgent) {
        try {
            auditLogRepository.createLog(userId, action, metadata, ipAddress, userAgent);
            log.debug("Audit log created: user={}, action={}", userId, action);
        } catch (Exception e) {
            log.error("Failed to create audit log", e);
            // Don't throw - audit failures shouldn't break business operations
        }
    }

    public List<AuditLogRepository.AuditLog> getUserAuditLogs(UUID userId, int limit, int offset) {
        return auditLogRepository.findByUserId(userId, limit, offset);
    }

    public List<AuditLogRepository.AuditLog> getAllAuditLogs(int limit, int offset) {
        return auditLogRepository.findAll(limit, offset);
    }
}
