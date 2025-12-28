package com.todoapp.application.service;

import com.todoapp.domain.exception.ForbiddenException;
import com.todoapp.infrastructure.jooq.enums.Role;
import com.todoapp.domain.repository.TodoRepository;
import com.todoapp.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthorizationService {

    private final UserService userService;

    public void ensureIsAdmin(UUID userId) {
        UserRepository.User user = userService.getUserById(userId);
        if (user.role() != Role.admin && user.role() != Role.sysadmin) {
            throw new ForbiddenException("Admin access required");
        }
    }

    public void ensureIsSysAdmin(UUID userId) {
        UserRepository.User user = userService.getUserById(userId);
        if (user.role() != Role.sysadmin) {
            throw new ForbiddenException("System admin access required");
        }
    }

    public void ensureCanAccessUserData(UUID currentUserId, UUID targetUserId) {
        if (currentUserId.equals(targetUserId)) {
            return; // Users can always access their own data
        }
        ensureIsAdmin(currentUserId);
    }

    public void ensureCanModifyUser(UUID currentUserId, UUID targetUserId) {
        UserRepository.User currentUser = userService.getUserById(currentUserId);

        if (currentUserId.equals(targetUserId)) {
            return; // Users can modify themselves
        }

        if (currentUser.role() == Role.sysadmin) {
            return; // Only sysadmins can modify other users
        }

        throw new ForbiddenException("Insufficient permissions to modify this user");
    }

    public void ensureCanAccessTodo(UUID currentUserId, TodoRepository.Todo todo) {
        if (todo.isOwnedBy(currentUserId)) {
            return; // Owner can access
        }
        ensureIsAdmin(currentUserId); // Admins can access any todo
    }

    public void ensureCanModifyTodo(UUID currentUserId, TodoRepository.Todo todo) {
        if (todo.isOwnedBy(currentUserId)) {
            return; // Owner can modify
        }

        // Only sysadmins can modify other users' todos
        ensureIsSysAdmin(currentUserId);
    }
}
