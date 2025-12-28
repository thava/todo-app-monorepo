package com.todoapp.application.service;

import com.todoapp.domain.exception.UnauthorizedException;
import com.todoapp.domain.repository.RefreshTokenRepository;
import com.todoapp.infrastructure.security.JwtService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class RefreshTokenService {

    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtService jwtService;

    @Transactional
    public String createRefreshToken(UUID userId, String ipAddress, String userAgent) {
        // Each refresh token gets a unique session ID
        UUID sessionId = UUID.randomUUID();
        String token = jwtService.generateRefreshToken(userId, sessionId);
        Instant expiresAt = Instant.now().plus(jwtService.getRefreshTokenDuration());

        refreshTokenRepository.saveToken(userId, token, expiresAt, ipAddress, userAgent);
        return token;
    }

    public UUID validateAndGetUserId(String token) {
        RefreshTokenRepository.RefreshToken refreshToken = refreshTokenRepository.findByToken(token)
            .orElseThrow(() -> new UnauthorizedException("Invalid or expired refresh token"));

        return refreshToken.userId();
    }

    @Transactional
    public void revokeToken(String token) {
        refreshTokenRepository.revokeToken(token);
    }

    @Transactional
    public void revokeAllUserTokens(UUID userId) {
        refreshTokenRepository.revokeAllUserTokens(userId);
    }

    @Scheduled(cron = "0 0 3 * * ?")
    @Transactional
    public void cleanupExpiredTokens() {
        log.info("Running scheduled cleanup of expired refresh tokens");
        refreshTokenRepository.deleteExpiredTokens();
    }
}
