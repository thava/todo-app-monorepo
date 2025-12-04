package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.tables.PasswordResetTokens;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.springframework.stereotype.Repository;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Repository
@RequiredArgsConstructor
public class PasswordResetTokenRepository {

    private final DSLContext dsl;
    private static final PasswordResetTokens TOKENS = PasswordResetTokens.PASSWORD_RESET_TOKENS;

    public void saveToken(UUID userId, String token, Instant expiresAt) {
        String tokenHash = hashToken(token);
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);
        OffsetDateTime expiresAtOdt = OffsetDateTime.ofInstant(expiresAt, ZoneOffset.UTC);

        dsl.insertInto(TOKENS)
            .set(TOKENS.USER_ID, userId)
            .set(TOKENS.TOKEN_HASH, tokenHash)
            .set(TOKENS.EXPIRES_AT, expiresAtOdt)
            .set(TOKENS.CREATED_AT, now)
            .execute();

        log.debug("Saved password reset token for user: {}", userId);
    }

    public Optional<PasswordResetToken> findByToken(String token) {
        String tokenHash = hashToken(token);

        return dsl.selectFrom(TOKENS)
            .where(TOKENS.TOKEN_HASH.eq(tokenHash))
            .and(TOKENS.USED_AT.isNull())
            .and(TOKENS.EXPIRES_AT.greaterThan(OffsetDateTime.now(ZoneOffset.UTC)))
            .fetchOptional()
            .map(record -> new PasswordResetToken(
                record.get(TOKENS.USER_ID),
                record.get(TOKENS.TOKEN_HASH)
            ));
    }

    public void markAsUsed(String token) {
        String tokenHash = hashToken(token);

        dsl.update(TOKENS)
            .set(TOKENS.USED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(TOKENS.TOKEN_HASH.eq(tokenHash))
            .execute();

        log.debug("Marked password reset token as used");
    }

    public void deleteExpiredTokens() {
        int deleted = dsl.deleteFrom(TOKENS)
            .where(TOKENS.EXPIRES_AT.lessThan(OffsetDateTime.now(ZoneOffset.UTC)))
            .execute();

        log.info("Deleted {} expired password reset tokens", deleted);
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
        } catch (Exception e) {
            throw new RuntimeException("Failed to hash token", e);
        }
    }

    public record PasswordResetToken(UUID userId, String tokenHash) {}
}
