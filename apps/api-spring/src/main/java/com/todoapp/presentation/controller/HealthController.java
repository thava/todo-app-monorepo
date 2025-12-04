package com.todoapp.presentation.controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.jooq.DSLContext;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Health Check Controller
 * Provides liveness and readiness probes
 */
@RestController
@RequiredArgsConstructor
@Tag(name = "health", description = "Health check endpoints")
public class HealthController {

    private final DSLContext dsl;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }

    @GetMapping("/readiness")
    public ResponseEntity<Map<String, Object>> readiness() {
        try {
            // Check database connection
            dsl.selectOne().fetch();
            return ResponseEntity.ok(Map.of(
                "status", "UP",
                "database", "connected"
            ));
        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of(
                "status", "DOWN",
                "database", "disconnected",
                "error", e.getMessage()
            ));
        }
    }
}
