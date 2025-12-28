package com.todoapp.interfaces.controller;

import com.todoapp.application.service.AuthorizationService;
import com.todoapp.application.service.UserService;
import com.todoapp.domain.repository.UserRepository;
import com.todoapp.infrastructure.security.CurrentUser;
import com.todoapp.infrastructure.security.JwtAuthenticationFilter;
import com.todoapp.interfaces.dto.user.UpdateProfileDto;
import com.todoapp.interfaces.dto.user.UserResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Slf4j
@RestController
@RequiredArgsConstructor
public class UsersController {

    private final UserService userService;
    private final AuthorizationService authorizationService;

    // Endpoint at /me (for test compatibility)
    @GetMapping("/me")
    public ResponseEntity<UserResponseDto> getCurrentUserAtRoot(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        UserRepository.User user = userService.getUserById(currentUser.userId());
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    // Endpoint at /users/me
    @GetMapping("/users/me")
    public ResponseEntity<UserResponseDto> getCurrentUser(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        UserRepository.User user = userService.getUserById(currentUser.userId());
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    @PatchMapping("/me")
    public ResponseEntity<UserResponseDto> updateProfileAtRoot(
            @Valid @RequestBody UpdateProfileDto dto,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        UserRepository.User user = userService.updateUser(
            currentUser.userId(),
            dto.email(),
            dto.password(),
            dto.fullName(),
            null,  // Don't allow changing role through profile update
            false
        );
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    @PatchMapping("/users/me")
    public ResponseEntity<UserResponseDto> updateProfile(
            @Valid @RequestBody UpdateProfileDto dto,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        UserRepository.User user = userService.updateUser(
            currentUser.userId(),
            dto.email(),
            dto.password(),
            dto.fullName(),
            null,
            false
        );
        
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    @GetMapping("/users/{userId}")
    public ResponseEntity<UserResponseDto> getUserById(
            @PathVariable UUID userId,
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser) {
        
        authorizationService.ensureCanAccessUserData(currentUser.userId(), userId);
        UserRepository.User user = userService.getUserById(userId);
        return ResponseEntity.ok(mapToUserResponseDto(user));
    }

    private UserResponseDto mapToUserResponseDto(UserRepository.User user) {
        return new UserResponseDto(
            user.id(),
            user.email(),
            user.fullName(),
            user.role(),
            user.emailVerifiedAt(),
            user.createdAt(),
            user.updatedAt()
        );
    }
}
