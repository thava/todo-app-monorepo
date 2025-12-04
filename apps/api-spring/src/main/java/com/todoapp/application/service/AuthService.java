package com.todoapp.application.service;

import com.todoapp.domain.exception.UnauthorizedException;
import com.todoapp.domain.model.Role;
import com.todoapp.domain.repository.UserRepository;
import com.todoapp.infrastructure.security.JwtService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserService userService;
    private final RefreshTokenService refreshTokenService;
    private final JwtService jwtService;
    private final AuditService auditService;
    private final EmailVerificationService emailVerificationService;

    @Transactional
    public AuthResponse register(String email, String password, String fullName, 
                                 String ipAddress, String userAgent) {
        UserRepository.User user = userService.registerUser(email, password, fullName, Role.USER);
        
        String accessToken = jwtService.generateAccessToken(user.id(), user.email(), user.role());
        String refreshToken = refreshTokenService.createRefreshToken(user.id(), ipAddress, userAgent);
        
        auditService.logAction(user.id(), "USER_REGISTERED", null, ipAddress, userAgent);
        
        // Send verification email asynchronously
        emailVerificationService.sendVerificationEmail(user.id(), user.email());
        
        return new AuthResponse(accessToken, refreshToken, user);
    }

    @Transactional
    public AuthResponse login(String email, String password, String ipAddress, String userAgent) {
        UserRepository.User user = userService.authenticate(email, password);
        
        String accessToken = jwtService.generateAccessToken(user.id(), user.email(), user.role());
        String refreshToken = refreshTokenService.createRefreshToken(user.id(), ipAddress, userAgent);
        
        auditService.logAction(user.id(), "USER_LOGIN", null, ipAddress, userAgent);
        
        return new AuthResponse(accessToken, refreshToken, user);
    }

    @Transactional
    public AuthResponse refreshToken(String refreshToken, String ipAddress, String userAgent) {
        UUID userId = refreshTokenService.validateAndGetUserId(refreshToken);
        UserRepository.User user = userService.getUserById(userId);
        
        // Revoke old token and create new one (token rotation)
        refreshTokenService.revokeToken(refreshToken);
        String newRefreshToken = refreshTokenService.createRefreshToken(userId, ipAddress, userAgent);
        
        String accessToken = jwtService.generateAccessToken(user.id(), user.email(), user.role());
        
        auditService.logAction(userId, "TOKEN_REFRESHED", null, ipAddress, userAgent);
        
        return new AuthResponse(accessToken, newRefreshToken, user);
    }

    @Transactional
    public void logout(String refreshToken, UUID userId, String ipAddress, String userAgent) {
        refreshTokenService.revokeToken(refreshToken);
        auditService.logAction(userId, "USER_LOGOUT", null, ipAddress, userAgent);
    }

    @Transactional
    public void logoutAll(UUID userId, String ipAddress, String userAgent) {
        refreshTokenService.revokeAllUserTokens(userId);
        auditService.logAction(userId, "USER_LOGOUT_ALL", null, ipAddress, userAgent);
    }

    public record AuthResponse(String accessToken, String refreshToken, UserRepository.User user) {}
}
