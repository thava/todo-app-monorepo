package com.todoapp.infrastructure.security;

import com.todoapp.infrastructure.jooq.enums.Role;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;

@Slf4j
@Service
public class JwtService {

    @Value("${jwt.access-secret}")
    private String accessTokenSecret;

    @Value("${jwt.refresh-secret}")
    private String refreshTokenSecret;

    @Value("${jwt.access-expiry:15m}")
    private String accessTokenExpiry;

    @Value("${jwt.refresh-expiry:7d}")
    private String refreshTokenExpiry;

    private SecretKey accessTokenKey;
    private SecretKey refreshTokenKey;

    @PostConstruct
    public void init() {
        this.accessTokenKey = Keys.hmacShaKeyFor(accessTokenSecret.getBytes(StandardCharsets.UTF_8));
        this.refreshTokenKey = Keys.hmacShaKeyFor(refreshTokenSecret.getBytes(StandardCharsets.UTF_8));
        log.info("JWT Service initialized with access expiry: {} and refresh expiry: {}", accessTokenExpiry, refreshTokenExpiry);
    }

    public String generateAccessToken(UUID userId, String email, Role role) {
        Instant now = Instant.now();
        Instant expiry = now.plus(parseDuration(accessTokenExpiry));

        return Jwts.builder()
            .subject(userId.toString())
            .claim("email", email)
            .claim("role", role.getLiteral())
            .claim("type", "access")
            .issuedAt(Date.from(now))
            .expiration(Date.from(expiry))
            .signWith(accessTokenKey)
            .compact();
    }

    public String generateRefreshToken(UUID userId, UUID sessionId) {
        Instant now = Instant.now();
        Instant expiry = now.plus(parseDuration(refreshTokenExpiry));

        return Jwts.builder()
            .subject(userId.toString())
            .claim("type", "refresh")
            .claim("sessionId", sessionId.toString())
            .issuedAt(Date.from(now))
            .expiration(Date.from(expiry))
            .signWith(refreshTokenKey)
            .compact();
    }

    public Claims validateAccessToken(String token) {
        return Jwts.parser()
            .verifyWith(accessTokenKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public Claims validateRefreshToken(String token) {
        return Jwts.parser()
            .verifyWith(refreshTokenKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public Duration getRefreshTokenDuration() {
        return parseDuration(refreshTokenExpiry);
    }

    private Duration parseDuration(String duration) {
        if (duration.endsWith("m")) {
            return Duration.ofMinutes(Long.parseLong(duration.substring(0, duration.length() - 1)));
        } else if (duration.endsWith("h")) {
            return Duration.ofHours(Long.parseLong(duration.substring(0, duration.length() - 1)));
        } else if (duration.endsWith("d")) {
            return Duration.ofDays(Long.parseLong(duration.substring(0, duration.length() - 1)));
        }
        throw new IllegalArgumentException("Invalid duration format: " + duration);
    }
}
