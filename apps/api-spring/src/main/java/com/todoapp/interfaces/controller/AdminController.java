package com.todoapp.interfaces.controller;

import com.todoapp.application.service.AuditService;
import com.todoapp.application.service.AuthorizationService;
import com.todoapp.application.service.MetricsService;
import com.todoapp.application.service.UserService;
import com.todoapp.domain.repository.AuditLogRepository;
import com.todoapp.domain.repository.UserRepository;
import com.todoapp.infrastructure.security.CurrentUser;
import com.todoapp.infrastructure.security.JwtAuthenticationFilter;
import com.todoapp.interfaces.dto.admin.AuditLogResponseDto;
import com.todoapp.interfaces.dto.admin.MetricsResponseDto;
import com.todoapp.interfaces.dto.user.UpdateUserDto;
import com.todoapp.interfaces.dto.user.UserResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping("/admin")
@RequiredArgsConstructor
public class AdminController {

    private final UserService userService;
    private final AuditService auditService;
    private final MetricsService metricsService;
    private final AuthorizationService authorizationService;

    @GetMapping("/users")
    public ResponseEntity<List<UserResponseDto>> getAllUsers(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureIsAdmin(currentUser.userId());
        List<UserRepository.User> users = userService.getAllUsers();
        return ResponseEntity.ok(users.stream().map(this::mapToUserResponseDto).toList());
    }

    @GetMapping("/users/{userId}")
    public ResponseEntity<UserResponseDto> getUserById(
            @PathVariable UUID userId,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureIsAdmin(currentUser.userId());
        UserRepository.User user = userService.getUserById(userId);
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    @PatchMapping("/users/{userId}")
    public ResponseEntity<UserResponseDto> updateUser(
            @PathVariable UUID userId,
            @Valid @RequestBody UpdateUserDto dto,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureCanModifyUser(currentUser.userId(), userId);
        
        UserRepository.User user = userService.updateUser(
            userId,
            dto.email(),
            dto.password(),
            dto.fullName(),
            dto.role(),
            dto.emailVerified() != null && dto.emailVerified()
        );
        
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    @DeleteMapping("/users/{userId}")
    public ResponseEntity<Void> deleteUser(
            @PathVariable UUID userId,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureCanModifyUser(currentUser.userId(), userId);
        userService.deleteUser(userId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/audit-logs")
    public ResponseEntity<List<AuditLogResponseDto>> getAllAuditLogs(
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(defaultValue = "0") int offset,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureIsAdmin(currentUser.userId());
        List<AuditLogRepository.AuditLog> logs = auditService.getAllAuditLogs(limit, offset);
        return ResponseEntity.ok(logs.stream().map(this::mapToAuditLogResponseDto).toList());
    }

    @GetMapping("/audit-logs/user/{userId}")
    public ResponseEntity<List<AuditLogResponseDto>> getUserAuditLogs(
            @PathVariable UUID userId,
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(defaultValue = "0") int offset,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureCanAccessUserData(currentUser.userId(), userId);
        List<AuditLogRepository.AuditLog> logs = auditService.getUserAuditLogs(userId, limit, offset);
        return ResponseEntity.ok(logs.stream().map(this::mapToAuditLogResponseDto).toList());
    }

    @GetMapping("/metrics")
    public ResponseEntity<MetricsResponseDto> getMetrics(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureIsAdmin(currentUser.userId());
        Map<String, Object> metrics = metricsService.getSystemMetrics();
        
        return ResponseEntity.ok(new MetricsResponseDto(
            ((Number) metrics.get("totalUsers")).longValue(),
            ((Number) metrics.get("totalTodos")).longValue(),
            ((Number) metrics.get("completedTodos")).longValue(),
            ((Number) metrics.get("totalAuditLogs")).longValue(),
            (Map<String, Long>) metrics.get("usersByRole"),
            (Map<String, Long>) metrics.get("todosByPriority")
        ));
    }

    private UserResponseDto mapToUserResponseDto(UserRepository.User user) {
        return new UserResponseDto(
            user.id(),
            user.email(),
            user.fullName(),
            user.role(),
            user.emailVerifiedAt(),
            user.createdAt(),
            user.updatedAt()
        );
    }

    private AuditLogResponseDto mapToAuditLogResponseDto(AuditLogRepository.AuditLog log) {
        return new AuditLogResponseDto(
            log.id(),
            log.userId(),
            log.action(),
            log.metadata(),
            log.ipAddress(),
            log.userAgent(),
            log.createdAt()
        );
    }
}
