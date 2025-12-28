package com.todoapp.domain.repository;

import com.todoapp.infrastructure.jooq.enums.Priority;
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

    public UUID createTodo(UUID ownerId, String description, Boolean completed, Priority priority, Instant dueDate) {
        OffsetDateTime dueDateOdt = dueDate != null ? OffsetDateTime.ofInstant(dueDate, ZoneOffset.UTC) : null;
        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        return dsl.insertInto(TODOS)
            .set(TODOS.OWNER_ID, ownerId)
            .set(TODOS.DESCRIPTION, description)
            .set(TODOS.COMPLETED, completed != null ? completed : false)
            .set(TODOS.PRIORITY, priority != null ? priority : Priority.medium)
            .set(TODOS.DUE_DATE, dueDateOdt)
            .set(TODOS.CREATED_AT, now)
            .set(TODOS.UPDATED_AT, now)
            .returning(TODOS.ID)
            .fetchOne()
            .getId();
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
            .set(TODOS.COMPLETED, todo.completed())
            .set(TODOS.PRIORITY, todo.priority())
            .set(TODOS.DUE_DATE, dueDateOdt)
            .set(TODOS.UPDATED_AT, OffsetDateTime.now(ZoneOffset.UTC))
            .where(TODOS.ID.eq(todo.id()))
            .execute();
    }

    public void deleteById(UUID id) {
        dsl.deleteFrom(TODOS)
            .where(TODOS.ID.eq(id))
            .execute();
    }

    public boolean existsById(UUID id) {
        return dsl.fetchExists(
            dsl.selectFrom(TODOS)
                .where(TODOS.ID.eq(id))
        );
    }

    private Todo mapToTodo(org.jooq.Record record) {
        return new Todo(
            record.get(TODOS.ID),
            record.get(TODOS.OWNER_ID),
            record.get(TODOS.DESCRIPTION),
            record.get(TODOS.COMPLETED),
            record.get(TODOS.PRIORITY),
            record.get(TODOS.DUE_DATE) != null ? record.get(TODOS.DUE_DATE).toInstant() : null,
            record.get(TODOS.CREATED_AT).toInstant(),
            record.get(TODOS.UPDATED_AT).toInstant()
        );
    }

    public record Todo(
        UUID id,
        UUID ownerId,
        String description,
        Boolean completed,
        Priority priority,
        Instant dueDate,
        Instant createdAt,
        Instant updatedAt
    ) {
        public boolean isOwnedBy(UUID userId) {
            return this.ownerId.equals(userId);
        }
    }
}
