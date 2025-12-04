package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.tables.RefreshTokens;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.springframework.stereotype.Repository;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Repository
@RequiredArgsConstructor
public class RefreshTokenRepository {

    private final DSLContext dsl;
    private static final RefreshTokens REFRESH_TOKENS = RefreshTokens.REFRESH_TOKENS;

    public void saveToken(UUID userId, String token, Instant expiresAt, String ipAddress, String userAgent) {
        String tokenHash = hashToken(token);
        OffsetDateTime expiresAtOdt = OffsetDateTime.ofInstant(expiresAt, ZoneOffset.UTC);
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        dsl.insertInto(REFRESH_TOKENS)
            .set(REFRESH_TOKENS.USER_ID, userId)
            .set(REFRESH_TOKENS.TOKEN_HASH, tokenHash)
            .set(REFRESH_TOKENS.EXPIRES_AT, expiresAtOdt)
            .set(REFRESH_TOKENS.IP_ADDRESS, ipAddress)
            .set(REFRESH_TOKENS.USER_AGENT, userAgent)
            .set(REFRESH_TOKENS.CREATED_AT, now)
            .execute();

        log.debug("Saved refresh token for user: {}", userId);
    }

    public Optional<RefreshToken> findByToken(String token) {
        String tokenHash = hashToken(token);

        return dsl.selectFrom(REFRESH_TOKENS)
            .where(REFRESH_TOKENS.TOKEN_HASH.eq(tokenHash))
            .and(REFRESH_TOKENS.REVOKED_AT.isNull())
            .and(REFRESH_TOKENS.EXPIRES_AT.greaterThan(OffsetDateTime.now(ZoneOffset.UTC)))
            .fetchOptional()
            .map(record -> new RefreshToken(
                record.get(REFRESH_TOKENS.USER_ID),
                record.get(REFRESH_TOKENS.TOKEN_HASH),
                record.get(REFRESH_TOKENS.EXPIRES_AT).toInstant()
            ));
    }

    public void revokeToken(String token) {
        String tokenHash = hashToken(token);

        dsl.update(REFRESH_TOKENS)
            .set(REFRESH_TOKENS.REVOKED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(REFRESH_TOKENS.TOKEN_HASH.eq(tokenHash))
            .execute();

        log.debug("Revoked refresh token");
    }

    public void revokeAllUserTokens(UUID userId) {
        dsl.update(REFRESH_TOKENS)
            .set(REFRESH_TOKENS.REVOKED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(REFRESH_TOKENS.USER_ID.eq(userId))
            .and(REFRESH_TOKENS.REVOKED_AT.isNull())
            .execute();

        log.debug("Revoked all tokens for user: {}", userId);
    }

    public void deleteExpiredTokens() {
        int deleted = dsl.deleteFrom(REFRESH_TOKENS)
            .where(REFRESH_TOKENS.EXPIRES_AT.lessThan(OffsetDateTime.now(ZoneOffset.UTC)))
            .execute();

        log.info("Deleted {} expired refresh tokens", deleted);
    }

    private String hashToken(String token) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(token.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    public record RefreshToken(UUID userId, String tokenHash, Instant expiresAt) {}
}
