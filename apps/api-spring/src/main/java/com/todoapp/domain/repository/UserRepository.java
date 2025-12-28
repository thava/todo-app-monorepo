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
            .set(USERS.EMAIL, email)
            .set(USERS.PASSWORD_HASH_PRIMARY, passwordHash)
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
        return dsl.selectFrom(USERS)
            .where(USERS.EMAIL.eq(email))
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
            .set(USERS.EMAIL, user.email())
            .set(USERS.PASSWORD_HASH_PRIMARY, user.passwordHash())
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
                .where(USERS.EMAIL.eq(email))
        );
    }

    private User mapToUser(org.jooq.Record record) {
        return new User(
            record.get(USERS.ID),
            record.get(USERS.EMAIL),
            record.get(USERS.PASSWORD_HASH_PRIMARY),
            record.get(USERS.FULL_NAME),
            record.get(USERS.ROLE),
            record.get(USERS.EMAIL_VERIFIED_AT) != null ?
                record.get(USERS.EMAIL_VERIFIED_AT).toInstant() : null,
            record.get(USERS.CREATED_AT).toInstant(),
            record.get(USERS.UPDATED_AT).toInstant()
        );
    }

    public record User(
        UUID id,
        String email,
        String passwordHash,
        String fullName,
        Role role,
        Instant emailVerifiedAt,
        Instant createdAt,
        Instant updatedAt
    ) {}
}
