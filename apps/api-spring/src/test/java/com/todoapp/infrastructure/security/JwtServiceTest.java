package com.todoapp.infrastructure.security;

import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Unit tests for JwtService
 */
class JwtServiceTest {

    private JwtService jwtService;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService(
            "test-access-secret-key-for-testing-only-min-32-bytes",
            "test-refresh-secret-key-for-testing-only-min-32-bytes",
            "15m",
            "7d"
        );
    }

    @Test
    void shouldGenerateAccessToken() {
        UUID userId = UUID.randomUUID();
        String email = "test@example.com";
        String role = "guest";

        String token = jwtService.generateAccessToken(userId, email, role);

        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
    }

    @Test
    void shouldGenerateRefreshToken() {
        UUID userId = UUID.randomUUID();

        String token = jwtService.generateRefreshToken(userId);

        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
    }

    @Test
    void shouldValidateAccessToken() {
        UUID userId = UUID.randomUUID();
        String email = "test@example.com";
        String role = "guest";

        String token = jwtService.generateAccessToken(userId, email, role);
        Claims claims = jwtService.validateAccessToken(token);

        assertThat(claims).isNotNull();
        assertThat(jwtService.extractUserId(claims)).isEqualTo(userId);
        assertThat(jwtService.extractEmail(claims)).isEqualTo(email);
        assertThat(jwtService.extractRole(claims)).isEqualTo(role);
    }

    @Test
    void shouldValidateRefreshToken() {
        UUID userId = UUID.randomUUID();

        String token = jwtService.generateRefreshToken(userId);
        Claims claims = jwtService.validateRefreshToken(token);

        assertThat(claims).isNotNull();
        assertThat(jwtService.extractUserId(claims)).isEqualTo(userId);
    }

    @Test
    void shouldRejectInvalidAccessToken() {
        String invalidToken = "invalid.jwt.token";

        assertThatThrownBy(() -> jwtService.validateAccessToken(invalidToken))
            .isInstanceOf(JwtValidationException.class)
            .hasMessageContaining("Invalid access token");
    }

    @Test
    void shouldRejectAccessTokenWithWrongSecret() {
        UUID userId = UUID.randomUUID();
        String token = jwtService.generateRefreshToken(userId);

        // Try to validate refresh token as access token
        assertThatThrownBy(() -> jwtService.validateAccessToken(token))
            .isInstanceOf(JwtValidationException.class);
    }

    @Test
    void shouldParseAccessTokenExpiry() {
        assertThat(jwtService.getAccessTokenExpiry().toMinutes()).isEqualTo(15);
    }

    @Test
    void shouldParseRefreshTokenExpiry() {
        assertThat(jwtService.getRefreshTokenExpiry().toDays()).isEqualTo(7);
    }
}
