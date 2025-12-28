package com.todoapp.infrastructure.security;

import com.todoapp.infrastructure.jooq.enums.Role;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

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
        jwtService = new JwtService();

        // Set private fields using ReflectionTestUtils
        ReflectionTestUtils.setField(jwtService, "accessTokenSecret",
            "test-access-secret-key-for-testing-only-min-32-bytes");
        ReflectionTestUtils.setField(jwtService, "refreshTokenSecret",
            "test-refresh-secret-key-for-testing-only-min-32-bytes");
        ReflectionTestUtils.setField(jwtService, "accessTokenExpiry", "15m");
        ReflectionTestUtils.setField(jwtService, "refreshTokenExpiry", "7d");

        // Call @PostConstruct method manually
        jwtService.init();
    }

    @Test
    void shouldGenerateAccessToken() {
        UUID userId = UUID.randomUUID();
        String email = "test@example.com";
        Role role = Role.guest;

        String token = jwtService.generateAccessToken(userId, email, role);

        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
    }

    @Test
    void shouldGenerateRefreshToken() {
        UUID userId = UUID.randomUUID();
        UUID sessionId = UUID.randomUUID();

        String token = jwtService.generateRefreshToken(userId, sessionId);

        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
    }

    @Test
    void shouldValidateAccessToken() {
        UUID userId = UUID.randomUUID();
        String email = "test@example.com";
        Role role = Role.guest;

        String token = jwtService.generateAccessToken(userId, email, role);
        Claims claims = jwtService.validateAccessToken(token);

        assertThat(claims).isNotNull();
        assertThat(claims.getSubject()).isEqualTo(userId.toString());
        assertThat(claims.get("email", String.class)).isEqualTo(email);
        assertThat(claims.get("role", String.class)).isEqualTo("guest");
        assertThat(claims.get("type", String.class)).isEqualTo("access");
    }

    @Test
    void shouldValidateRefreshToken() {
        UUID userId = UUID.randomUUID();
        UUID sessionId = UUID.randomUUID();

        String token = jwtService.generateRefreshToken(userId, sessionId);
        Claims claims = jwtService.validateRefreshToken(token);

        assertThat(claims).isNotNull();
        assertThat(claims.getSubject()).isEqualTo(userId.toString());
        assertThat(claims.get("type", String.class)).isEqualTo("refresh");
        assertThat(claims.get("sessionId", String.class)).isEqualTo(sessionId.toString());
    }

    @Test
    void shouldRejectInvalidAccessToken() {
        String invalidToken = "invalid.jwt.token";

        assertThatThrownBy(() -> jwtService.validateAccessToken(invalidToken))
            .hasMessageContaining("JWT");
    }

    @Test
    void shouldRejectAccessTokenWithWrongSecret() {
        UUID userId = UUID.randomUUID();
        UUID sessionId = UUID.randomUUID();
        String token = jwtService.generateRefreshToken(userId, sessionId);

        // Try to validate refresh token as access token (different secret)
        assertThatThrownBy(() -> jwtService.validateAccessToken(token))
            .isInstanceOf(Exception.class);
    }

    @Test
    void shouldParseRefreshTokenDuration() {
        assertThat(jwtService.getRefreshTokenDuration().toDays()).isEqualTo(7);
    }
}
