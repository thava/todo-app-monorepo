package com.todoapp.interfaces.controller;

import com.todoapp.application.service.AuthService;
import com.todoapp.application.service.EmailVerificationService;
import com.todoapp.application.service.PasswordResetService;
import com.todoapp.domain.repository.UserRepository;
import com.todoapp.infrastructure.security.CurrentUser;
import com.todoapp.infrastructure.security.JwtAuthenticationFilter;
import com.todoapp.interfaces.dto.auth.*;
import com.todoapp.interfaces.dto.user.UserInfoDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final EmailVerificationService emailVerificationService;
    private final PasswordResetService passwordResetService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponseDto> register(
            @Valid @RequestBody RegisterDto dto,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        AuthService.AuthResponse response = authService.register(
            dto.email(), dto.password(), dto.fullName(), dto.role(), dto.autoverify(), ipAddress, userAgent);

        return ResponseEntity.status(HttpStatus.CREATED).body(mapToAuthResponseDto(response));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDto> login(
            @Valid @RequestBody LoginDto dto,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        AuthService.AuthResponse response = authService.login(
            dto.email(), dto.password(), ipAddress, userAgent);
        
        return ResponseEntity.ok(mapToAuthResponseDto(response));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponseDto> refresh(
            @Valid @RequestBody RefreshTokenDto dto,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        AuthService.AuthResponse response = authService.refreshToken(
            dto.refreshToken(), ipAddress, userAgent);
        
        return ResponseEntity.ok(mapToAuthResponseDto(response));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(
            @Valid @RequestBody RefreshTokenDto dto,
            HttpServletRequest request) {

        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");

        // Get userId from refresh token and logout
        authService.logoutWithRefreshToken(dto.refreshToken(), ipAddress, userAgent);

        return ResponseEntity.noContent().build();
    }

    @PostMapping("/logout-all")
    public ResponseEntity<Map<String, String>> logoutAll(
            @CurrentUser JwtAuthenticationFilter.UserPrincipal currentUser,
            HttpServletRequest request) {
        
        String ipAddress = getClientIp(request);
        String userAgent = request.getHeader("User-Agent");
        
        authService.logoutAll(currentUser.userId(), ipAddress, userAgent);
        
        return ResponseEntity.ok(Map.of("message", "Logged out from all devices successfully"));
    }

    @PostMapping("/verify-email")
    public ResponseEntity<Map<String, String>> verifyEmail(@Valid @RequestBody VerifyEmailDto dto) {
        emailVerificationService.verifyEmail(dto.token());
        return ResponseEntity.ok(Map.of("message", "Email verified successfully"));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<Map<String, String>> forgotPassword(@Valid @RequestBody ForgotPasswordDto dto) {
        passwordResetService.requestPasswordReset(dto.email());
        return ResponseEntity.ok(Map.of("message", "Password reset email sent if account exists"));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<Map<String, String>> resetPassword(@Valid @RequestBody ResetPasswordDto dto) {
        passwordResetService.resetPassword(dto.token(), dto.newPassword());
        return ResponseEntity.ok(Map.of("message", "Password reset successfully"));
    }

    private String getClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }

    private AuthResponseDto mapToAuthResponseDto(AuthService.AuthResponse response) {
        UserRepository.User user = response.user();
        UserInfoDto userDto = new UserInfoDto(
            user.id(),
            user.email(),
            user.fullName(),
            user.role(),
            user.emailVerifiedAt(),
            user.localUsername(),
            user.googleEmail(),
            user.msEmail(),
            user.createdAt(),
            user.updatedAt()
        );

        return new AuthResponseDto(response.accessToken(), response.refreshToken(), userDto);
    }
}
