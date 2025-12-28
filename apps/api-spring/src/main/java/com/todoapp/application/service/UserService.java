package com.todoapp.application.service;

import com.todoapp.domain.exception.BadRequestException;
import com.todoapp.domain.exception.NotFoundException;
import com.todoapp.domain.exception.UnauthorizedException;
import com.todoapp.infrastructure.jooq.enums.Role;
import com.todoapp.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public UserRepository.User registerUser(String email, String password, String fullName, Role role) {
        if (userRepository.existsByEmail(email)) {
            throw new BadRequestException("Email already registered");
        }

        String hashedPassword = passwordEncoder.encode(password);
        UUID userId = userRepository.createUser(email, hashedPassword, fullName, role);

        return userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("Failed to create user"));
    }

    public UserRepository.User authenticate(String email, String password) {
        UserRepository.User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new UnauthorizedException("Invalid credentials"));

        if (!passwordEncoder.matches(password, user.passwordHash())) {
            throw new UnauthorizedException("Invalid credentials");
        }

        return user;
    }

    public UserRepository.User getUserById(UUID userId) {
        return userRepository.findById(userId)
            .orElseThrow(() -> new NotFoundException("User not found"));
    }

    public List<UserRepository.User> getAllUsers() {
        return userRepository.findAll();
    }

    @Transactional
    public UserRepository.User updateUser(UUID userId, String email, String password,
                                         String fullName, Role role, boolean emailVerified) {
        UserRepository.User user = getUserById(userId);

        if (email != null && !email.equals(user.email())) {
            if (userRepository.existsByEmail(email)) {
                throw new BadRequestException("Email already in use");
            }
        }

        String newEmail = email != null ? email : user.email();
        String newPasswordHash = password != null ? passwordEncoder.encode(password) : user.passwordHash();
        String newFullName = fullName != null ? fullName : user.fullName();
        Role newRole = role != null ? role : user.role();
        var newEmailVerifiedAt = emailVerified ? 
            (user.emailVerifiedAt() != null ? user.emailVerifiedAt() : java.time.Instant.now()) : 
            user.emailVerifiedAt();

        UserRepository.User updatedUser = new UserRepository.User(
            user.id(),
            newEmail,
            newPasswordHash,
            newFullName,
            newRole,
            newEmailVerifiedAt,
            user.createdAt(),
            user.updatedAt()
        );

        userRepository.update(updatedUser);
        return userRepository.findById(userId)
            .orElseThrow(() -> new NotFoundException("User not found"));
    }

    @Transactional
    public void deleteUser(UUID userId) {
        if (!userRepository.findById(userId).isPresent()) {
            throw new NotFoundException("User not found");
        }
        userRepository.deleteById(userId);
    }

    @Transactional
    public void verifyEmail(UUID userId) {
        if (!userRepository.findById(userId).isPresent()) {
            throw new NotFoundException("User not found");
        }
        userRepository.markEmailVerified(userId);
        log.info("Email verified for user {}", userId);
    }
}
