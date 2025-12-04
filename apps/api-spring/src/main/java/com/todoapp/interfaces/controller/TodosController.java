package com.todoapp.interfaces.controller;

import com.todoapp.application.service.TodoService;
import com.todoapp.domain.repository.TodoRepository;
import com.todoapp.infrastructure.security.CurrentUser;
import com.todoapp.infrastructure.security.JwtAuthenticationFilter;
import com.todoapp.interfaces.dto.todo.CreateTodoDto;
import com.todoapp.interfaces.dto.todo.TodoResponseDto;
import com.todoapp.interfaces.dto.todo.UpdateTodoDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping("/todos")
@RequiredArgsConstructor
public class TodosController {

    private final TodoService todoService;

    @PostMapping
    public ResponseEntity<TodoResponseDto> createTodo(
            @Valid @RequestBody CreateTodoDto dto,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        TodoRepository.Todo todo = todoService.createTodo(
            currentUser.userId(),
            dto.title(),
            dto.description(),
            dto.priority(),
            dto.dueDate(),
            ipAddress,
            userAgent
        );
        
        return ResponseEntity.status(HttpStatus.CREATED).body(mapToTodoResponseDto(todo));
    }

    @GetMapping("/{id}")
    public ResponseEntity<TodoResponseDto> getTodoById(
            @PathVariable UUID id,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        TodoRepository.Todo todo = todoService.getTodoById(id, currentUser.userId());
        return ResponseEntity.ok(mapToTodoResponseDto(todo));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<TodoResponseDto>> getUserTodos(
            @PathVariable UUID userId,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        List<TodoRepository.Todo> todos = todoService.getUserTodos(userId, currentUser.userId());
        return ResponseEntity.ok(todos.stream().map(this::mapToTodoResponseDto).toList());
    }

    @GetMapping
    public ResponseEntity<List<TodoResponseDto>> getAllTodos(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        List<TodoRepository.Todo> todos = todoService.getAllTodos(currentUser.userId());
        return ResponseEntity.ok(todos.stream().map(this::mapToTodoResponseDto).toList());
    }

    @PatchMapping("/{id}")
    public ResponseEntity<TodoResponseDto> updateTodo(
            @PathVariable UUID id,
            @Valid @RequestBody UpdateTodoDto dto,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        TodoRepository.Todo todo = todoService.updateTodo(
            id,
            currentUser.userId(),
            dto.title(),
            dto.description(),
            dto.priority(),
            dto.completed(),
            dto.dueDate(),
            ipAddress,
            userAgent
        );
        
        return ResponseEntity.ok(mapToTodoResponseDto(todo));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTodo(
            @PathVariable UUID id,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        todoService.deleteTodo(id, currentUser.userId(), ipAddress, userAgent);
        return ResponseEntity.noContent().build();
    }

    private String getClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }

    private TodoResponseDto mapToTodoResponseDto(TodoRepository.Todo todo) {
        return new TodoResponseDto(
            todo.id(),
            todo.ownerId(),
            todo.title(),
            todo.description(),
            todo.priority(),
            todo.completed(),
            todo.dueDate(),
            todo.createdAt(),
            todo.updatedAt()
        );
    }
}
