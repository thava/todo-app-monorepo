package com.todoapp.application.service;

import com.todoapp.domain.exception.BadRequestException;
import com.todoapp.domain.exception.NotFoundException;
import com.todoapp.domain.repository.PasswordResetTokenRepository;
import com.todoapp.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class PasswordResetService {

    private final PasswordResetTokenRepository tokenRepository;
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    @Value("${app.base-url:http://localhost:3000}")
    private String baseUrl;

    @Value("${app.password-reset-ttl:1h}")
    private String resetTtl;

    @Async
    @Transactional
    public void requestPasswordReset(String email) {
        UserRepository.User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new NotFoundException("User not found"));
        
        String token = generateToken();
        Instant expiresAt = Instant.now().plus(parseDuration(resetTtl));
        
        tokenRepository.saveToken(user.id(), token, expiresAt);
        
        String resetUrl = baseUrl + "/reset-password?token=" + token;
        String subject = "Reset your password";
        String htmlContent = buildPasswordResetEmail(resetUrl);
        
        emailService.sendEmail(email, subject, htmlContent);
        
        log.info("Password reset email sent to: {}", email);
    }

    @Transactional
    public void resetPassword(String token, String newPassword) {
        PasswordResetTokenRepository.PasswordResetToken resetToken = 
            tokenRepository.findByToken(token)
                .orElseThrow(() -> new BadRequestException("Invalid or expired reset token"));
        
        UserRepository.User user = userRepository.findById(resetToken.userId())
            .orElseThrow(() -> new NotFoundException("User not found"));
        
        String hashedPassword = passwordEncoder.encode(newPassword);
        
        UserRepository.User updatedUser = new UserRepository.User(
            user.id(),
            user.email(),
            user.fullName(),
            user.role(),
            user.emailVerifiedAt(),
            user.localUsername(),
            hashedPassword,
            user.localEnabled(),
            user.googleSub(),
            user.googleEmail(),
            user.msOid(),
            user.msTid(),
            user.msEmail(),
            user.createdAt(),
            user.updatedAt()
        );
        
        userRepository.update(updatedUser);
        tokenRepository.markAsUsed(token);
        
        log.info("Password reset completed for user: {}", user.id());
    }

    @Scheduled(cron = "0 0 5 * * ?")
    @Transactional
    public void cleanupExpiredTokens() {
        log.info("Running scheduled cleanup of expired password reset tokens");
        tokenRepository.deleteExpiredTokens();
    }

    private String generateToken() {
        return UUID.randomUUID().toString() + UUID.randomUUID().toString().replace("-", "");
    }

    private Duration parseDuration(String duration) {
        String value = duration.substring(0, duration.length() - 1);
        char unit = duration.charAt(duration.length() - 1);
        
        return switch (unit) {
            case 's' -> Duration.ofSeconds(Long.parseLong(value));
            case 'm' -> Duration.ofMinutes(Long.parseLong(value));
            case 'h' -> Duration.ofHours(Long.parseLong(value));
            case 'd' -> Duration.ofDays(Long.parseLong(value));
            default -> throw new IllegalArgumentException("Invalid duration format: " + duration);
        };
    }

    private String buildPasswordResetEmail(String resetUrl) {
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Reset Your Password</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password for your Todo App account.</p>
                    <p>Click the button below to reset your password:</p>
                    <div style="margin: 30px 0;">
                        <a href="%s" 
                           style="background-color: #2196F3; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 4px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">%s</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #999;">
                        This link will expire in 1 hour.
                    </p>
                    <p style="font-size: 12px; color: #999;">
                        If you didn't request a password reset, you can safely ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """.formatted(resetUrl, resetUrl);
    }
}
