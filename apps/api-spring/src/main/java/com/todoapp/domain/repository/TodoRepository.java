package com.todoapp.domain.repository;

import com.todoapp.domain.model.Priority;
import com.todoapp.infrastructure.jooq.tables.Todos;
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
public class TodoRepository {

    private final DSLContext dsl;
    private static final Todos TODOS = Todos.TODOS;

    public UUID createTodo(UUID ownerId, String description, Instant dueDate, Priority priority) {
        UUID id = UUID.randomUUID();
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);
        OffsetDateTime dueDateOdt = dueDate != null ? OffsetDateTime.ofInstant(dueDate, ZoneOffset.UTC) : null;

        dsl.insertInto(TODOS)
            .set(TODOS.ID, id)
            .set(TODOS.OWNER_ID, ownerId)
            .set(TODOS.DESCRIPTION, description)
            .set(TODOS.DUE_DATE, dueDateOdt)
            .set(TODOS.PRIORITY, priority.getValue())
            .set(TODOS.CREATED_AT, now)
            .set(TODOS.UPDATED_AT, now)
            .execute();

        log.debug("Created todo: {}", id);
        return id;
    }

    public Optional<Todo> findById(UUID id) {
        return dsl.selectFrom(TODOS)
            .where(TODOS.ID.eq(id))
            .fetchOptional()
            .map(this::mapToTodo);
    }

    public List<Todo> findAllByOwnerId(UUID ownerId) {
        return dsl.selectFrom(TODOS)
            .where(TODOS.OWNER_ID.eq(ownerId))
            .orderBy(TODOS.CREATED_AT.desc())
            .fetch()
            .map(this::mapToTodo);
    }

    public List<Todo> findAll() {
        return dsl.selectFrom(TODOS)
            .orderBy(TODOS.CREATED_AT.desc())
            .fetch()
            .map(this::mapToTodo);
    }

    public void update(Todo todo) {
        OffsetDateTime dueDateOdt = todo.dueDate() != null ?
            OffsetDateTime.ofInstant(todo.dueDate(), ZoneOffset.UTC) : null;

        dsl.update(TODOS)
            .set(TODOS.DESCRIPTION, todo.description())
            .set(TODOS.DUE_DATE, dueDateOdt)
            .set(TODOS.PRIORITY, todo.priority().getValue())
            .set(TODOS.UPDATED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(TODOS.ID.eq(todo.id()))
            .execute();

        log.debug("Updated todo: {}", todo.id());
    }

    public void deleteById(UUID id) {
        dsl.deleteFrom(TODOS)
            .where(TODOS.ID.eq(id))
            .execute();
        log.debug("Deleted todo: {}", id);
    }

    public boolean existsById(UUID id) {
        return dsl.fetchExists(
            dsl.selectOne().from(TODOS).where(TODOS.ID.eq(id))
        );
    }

    private Todo mapToTodo(org.jooq.Record record) {
        return new Todo(
            record.get(TODOS.ID),
            record.get(TODOS.OWNER_ID),
            record.get(TODOS.DESCRIPTION),
            record.get(TODOS.DUE_DATE) != null ? record.get(TODOS.DUE_DATE).toInstant() : null,
            Priority.fromValue(record.get(TODOS.PRIORITY)),
            record.get(TODOS.CREATED_AT).toInstant(),
            record.get(TODOS.UPDATED_AT).toInstant()
        );
    }

    public record Todo(
        UUID id,
        UUID ownerId,
        String description,
        Instant dueDate,
        Priority priority,
        Instant createdAt,
        Instant updatedAt
    ) {
        public boolean isOwnedBy(UUID userId) {
            return this.ownerId.equals(userId);
        }
    }
}
