package com.todoapp.application.service;

import com.todoapp.domain.exception.ForbiddenException;
import com.todoapp.domain.exception.NotFoundException;
import com.todoapp.infrastructure.jooq.enums.Priority;
import com.todoapp.domain.repository.TodoRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class TodoService {

    private final TodoRepository todoRepository;
    private final AuthorizationService authorizationService;
    private final AuditService auditService;
    private final UserService userService;

    @Transactional
    public TodoRepository.Todo createTodo(UUID ownerId, String description,
                                          Priority priority, Instant dueDate,
                                          String ipAddress, String userAgent) {
        UUID todoId = todoRepository.createTodo(ownerId, description, false, priority, dueDate);

        auditService.logAction(ownerId, "TODO_CREATED",
            String.format("{\"todoId\":\"%s\",\"description\":\"%s\"}", todoId, description),
            ipAddress, userAgent);

        return todoRepository.findById(todoId)
            .orElseThrow(() -> new RuntimeException("Failed to create todo"));
    }

    public TodoRepository.Todo getTodoById(UUID todoId, UUID currentUserId) {
        TodoRepository.Todo todo = todoRepository.findById(todoId)
            .orElseThrow(() -> new NotFoundException("Todo not found"));
        
        authorizationService.ensureCanAccessTodo(currentUserId, todo);
        
        return todo;
    }

    public List<TodoRepository.Todo> getUserTodos(UUID userId, UUID currentUserId) {
        authorizationService.ensureCanAccessUserData(currentUserId, userId);
        return todoRepository.findAllByOwnerId(userId);
    }

    public List<TodoRepository.Todo> getAllTodos(UUID currentUserId) {
        var currentUser = userService.getUserById(currentUserId);

        // Admins and sysadmins can see all todos
        if (currentUser.role() == com.todoapp.infrastructure.jooq.enums.Role.admin ||
            currentUser.role() == com.todoapp.infrastructure.jooq.enums.Role.sysadmin) {
            return todoRepository.findAll();
        }

        // Regular users see only their own todos
        return todoRepository.findAllByOwnerId(currentUserId);
    }

    @Transactional
    public TodoRepository.Todo updateTodo(UUID todoId, UUID currentUserId,
                                         String description,
                                         Priority priority, Boolean completed,
                                         Instant dueDate,
                                         String ipAddress, String userAgent) {
        TodoRepository.Todo existingTodo = todoRepository.findById(todoId)
            .orElseThrow(() -> new NotFoundException("Todo not found"));

        authorizationService.ensureCanModifyTodo(currentUserId, existingTodo);

        String newDescription = description != null ? description : existingTodo.description();
        Priority newPriority = priority != null ? priority : existingTodo.priority();
        Boolean newCompleted = completed != null ? completed : existingTodo.completed();
        Instant newDueDate = dueDate != null ? dueDate : existingTodo.dueDate();

        TodoRepository.Todo updatedTodo = new TodoRepository.Todo(
            existingTodo.id(),
            existingTodo.ownerId(),
            newDescription,
            newCompleted,
            newPriority,
            newDueDate,
            existingTodo.createdAt(),
            existingTodo.updatedAt()
        );

        todoRepository.update(updatedTodo);

        auditService.logAction(currentUserId, "TODO_UPDATED",
            String.format("{\"todoId\":\"%s\"}", todoId),
            ipAddress, userAgent);

        return todoRepository.findById(todoId)
            .orElseThrow(() -> new NotFoundException("Todo not found"));
    }

    @Transactional
    public void deleteTodo(UUID todoId, UUID currentUserId, String ipAddress, String userAgent) {
        TodoRepository.Todo todo = todoRepository.findById(todoId)
            .orElseThrow(() -> new NotFoundException("Todo not found"));
        
        authorizationService.ensureCanModifyTodo(currentUserId, todo);
        
        todoRepository.deleteById(todoId);
        
        auditService.logAction(currentUserId, "TODO_DELETED",
            String.format("{\"todoId\":\"%s\"}", todoId),
            ipAddress, userAgent);
    }
}
