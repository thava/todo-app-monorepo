package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.enums.Role;
import com.todoapp.infrastructure.jooq.tables.Users;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Repository
@RequiredArgsConstructor
public class UserRepository {

    private final DSLContext dsl;
    private static final Users USERS = Users.USERS;

    public UUID createUser(String email, String passwordHash, String fullName, Role role) {
        UUID id = UUID.randomUUID();
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        dsl.insertInto(USERS)
            .set(USERS.ID, id)
            .set(USERS.LOCAL_USERNAME, email)
            .set(USERS.LOCAL_PASSWORD_HASH, passwordHash)
            .set(USERS.LOCAL_ENABLED, true)
            .set(USERS.FULL_NAME, fullName)
            .set(USERS.ROLE, role)
            .set(USERS.CREATED_AT, now)
            .set(USERS.UPDATED_AT, now)
            .execute();

        log.debug("Created user: {}", id);
        return id;
    }

    public Optional<User> findById(UUID id) {
        return dsl.selectFrom(USERS)
            .where(USERS.ID.eq(id))
            .fetchOptional()
            .map(this::mapToUser);
    }

    public Optional<User> findByEmail(String email) {
        // Search by local_username for backward compatibility
        return dsl.selectFrom(USERS)
            .where(USERS.LOCAL_USERNAME.eq(email))
            .fetchOptional()
            .map(this::mapToUser);
    }

    public Optional<User> findByGoogleSub(String googleSub) {
        return dsl.selectFrom(USERS)
            .where(USERS.GOOGLE_SUB.eq(googleSub))
            .fetchOptional()
            .map(this::mapToUser);
    }

    public Optional<User> findByMicrosoftIdentity(UUID msOid, UUID msTid) {
        return dsl.selectFrom(USERS)
            .where(USERS.MS_OID.eq(msOid).and(USERS.MS_TID.eq(msTid)))
            .fetchOptional()
            .map(this::mapToUser);
    }

    public List<User> findAll() {
        return dsl.selectFrom(USERS)
            .orderBy(USERS.CREATED_AT.desc())
            .fetch()
            .map(this::mapToUser);
    }

    public void update(User user) {
        dsl.update(USERS)
            .set(USERS.LOCAL_USERNAME, user.localUsername())
            .set(USERS.LOCAL_PASSWORD_HASH, user.localPasswordHash())
            .set(USERS.LOCAL_ENABLED, user.localEnabled())
            .set(USERS.GOOGLE_SUB, user.googleSub())
            .set(USERS.GOOGLE_EMAIL, user.googleEmail())
            .set(USERS.MS_OID, user.msOid())
            .set(USERS.MS_TID, user.msTid())
            .set(USERS.MS_EMAIL, user.msEmail())
            .set(USERS.FULL_NAME, user.fullName())
            .set(USERS.ROLE, user.role())
            .set(USERS.EMAIL_VERIFIED_AT, user.emailVerifiedAt() != null ?
                OffsetDateTime.ofInstant(user.emailVerifiedAt(), ZoneOffset.UTC) : null)
            .set(USERS.UPDATED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(USERS.ID.eq(user.id()))
            .execute();

        log.debug("Updated user {}", user.id());
    }

    public void markEmailVerified(UUID userId) {
        dsl.update(USERS)
            .set(USERS.EMAIL_VERIFIED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .set(USERS.UPDATED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(USERS.ID.eq(userId))
            .execute();
        log.debug("Marked email verified for user {}", userId);
    }

    public void deleteById(UUID id) {
        dsl.deleteFrom(USERS)
            .where(USERS.ID.eq(id))
            .execute();
        log.debug("Deleted user {}", id);
    }

    public boolean existsByEmail(String email) {
        return dsl.fetchExists(
            dsl.selectOne()
                .from(USERS)
                .where(USERS.LOCAL_USERNAME.eq(email))
        );
    }

    private User mapToUser(org.jooq.Record record) {
        // Compute primary email from available identities
        String email = record.get(USERS.LOCAL_USERNAME);
        if (email == null) {
            email = record.get(USERS.GOOGLE_EMAIL);
        }
        if (email == null) {
            email = record.get(USERS.MS_EMAIL);
        }
        if (email == null) {
            email = "";
        }

        return new User(
            record.get(USERS.ID),
            email,
            record.get(USERS.FULL_NAME),
            record.get(USERS.ROLE),
            record.get(USERS.EMAIL_VERIFIED_AT) != null ?
                record.get(USERS.EMAIL_VERIFIED_AT).toInstant() : null,
            record.get(USERS.LOCAL_USERNAME),
            record.get(USERS.LOCAL_PASSWORD_HASH),
            record.get(USERS.LOCAL_ENABLED),
            record.get(USERS.GOOGLE_SUB),
            record.get(USERS.GOOGLE_EMAIL),
            record.get(USERS.MS_OID),
            record.get(USERS.MS_TID),
            record.get(USERS.MS_EMAIL),
            record.get(USERS.CREATED_AT).toInstant(),
            record.get(USERS.UPDATED_AT).toInstant()
        );
    }

    public record User(
        UUID id,
        String email,  // Computed from local/google/ms emails
        String fullName,
        Role role,
        Instant emailVerifiedAt,
        String localUsername,
        String localPasswordHash,
        Boolean localEnabled,
        String googleSub,
        String googleEmail,
        UUID msOid,
        UUID msTid,
        String msEmail,
        Instant createdAt,
        Instant updatedAt
    ) {}
}
