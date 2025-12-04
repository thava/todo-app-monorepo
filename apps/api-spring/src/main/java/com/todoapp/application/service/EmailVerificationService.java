package com.todoapp.application.service;

import com.todoapp.domain.exception.BadRequestException;
import com.todoapp.domain.repository.EmailVerificationTokenRepository;
import com.todoapp.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailVerificationService {

    private final EmailVerificationTokenRepository tokenRepository;
    private final UserRepository userRepository;
    private final EmailService emailService;

    @Value("${app.base-url:http://localhost:3000}")
    private String baseUrl;

    @Value("${app.email-verification-ttl:24h}")
    private String verificationTtl;

    @Async
    public void sendVerificationEmail(UUID userId, String email) {
        String token = generateToken();
        Instant expiresAt = Instant.now().plus(parseDuration(verificationTtl));
        
        tokenRepository.saveToken(userId, token, expiresAt);
        
        String verificationUrl = baseUrl + "/verify-email?token=" + token;
        String subject = "Verify your email address";
        String htmlContent = buildVerificationEmail(verificationUrl);
        
        emailService.sendEmail(email, subject, htmlContent);
        
        log.info("Verification email sent to: {}", email);
    }

    @Transactional
    public void verifyEmail(String token) {
        EmailVerificationTokenRepository.EmailVerificationToken verificationToken = 
            tokenRepository.findByToken(token)
                .orElseThrow(() -> new BadRequestException("Invalid or expired verification token"));
        
        userRepository.markEmailVerified(verificationToken.userId());
        tokenRepository.markAsUsed(token);
        
        log.info("Email verified for user: {}", verificationToken.userId());
    }

    @Scheduled(cron = "0 0 4 * * ?")
    @Transactional
    public void cleanupExpiredTokens() {
        log.info("Running scheduled cleanup of expired email verification tokens");
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

    private String buildVerificationEmail(String verificationUrl) {
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Verify Your Email</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering with Todo App!</p>
                    <p>Please click the button below to verify your email address:</p>
                    <div style="margin: 30px 0;">
                        <a href="%s" 
                           style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 4px; display: inline-block;">
                            Verify Email
                        </a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">%s</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #999;">
                        If you didn't create an account, you can safely ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """.formatted(verificationUrl, verificationUrl);
    }
}
