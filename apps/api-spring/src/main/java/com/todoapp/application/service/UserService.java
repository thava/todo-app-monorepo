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
    private final AuditService auditService;

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

        if (!user.localEnabled() || user.localPasswordHash() == null) {
            throw new UnauthorizedException("Local authentication disabled for this user");
        }

        if (!passwordEncoder.matches(password, user.localPasswordHash())) {
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
                                         String fullName, Role role, boolean emailVerified, Boolean unlinkLocal) {
        UserRepository.User user = getUserById(userId);

        if (email != null && !email.equals(user.localUsername())) {
            if (userRepository.existsByEmail(email)) {
                throw new BadRequestException("Email already in use");
            }
        }

        // Handle unlinkLocal
        String newLocalUsername = user.localUsername();
        String newPasswordHash = user.localPasswordHash();
        Boolean newLocalEnabled = user.localEnabled();

        if (Boolean.TRUE.equals(unlinkLocal)) {
            // Check if user has at least one other identity (Google or Microsoft)
            boolean hasGoogleIdentity = user.googleSub() != null;
            boolean hasMicrosoftIdentity = user.msOid() != null && user.msTid() != null;

            if (!hasGoogleIdentity && !hasMicrosoftIdentity) {
                throw new BadRequestException(
                    "Cannot unlink local account. You must have at least one other authentication method (Google or Microsoft) linked."
                );
            }

            // Check if local account is already unlinked
            if (!user.localEnabled() || user.localUsername() == null) {
                throw new BadRequestException("Local account is not linked");
            }

            // Unlink local account
            newLocalEnabled = false;
            newLocalUsername = null;
            newPasswordHash = null;
        } else {
            // Normal update flow
            newLocalUsername = email != null ? email : user.localUsername();
            newPasswordHash = password != null ? passwordEncoder.encode(password) : user.localPasswordHash();
        }

        String newFullName = fullName != null ? fullName : user.fullName();
        Role newRole = role != null ? role : user.role();
        var newEmailVerifiedAt = emailVerified ?
            (user.emailVerifiedAt() != null ? user.emailVerifiedAt() : java.time.Instant.now()) :
            user.emailVerifiedAt();

        UserRepository.User updatedUser = new UserRepository.User(
            user.id(),
            user.email(), // Computed field
            newFullName,
            newRole,
            newEmailVerifiedAt,
            newLocalUsername,
            newPasswordHash,
            newLocalEnabled,
            user.googleSub(),
            user.googleEmail(),
            user.msOid(),
            user.msTid(),
            user.msEmail(),
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

    @Transactional
    public java.util.Map<String, Object> mergeUsers(UUID sourceUserId, UUID destinationUserId,
                                                     String ipAddress, String userAgent) {
        // Validate that source and destination are different
        if (sourceUserId.equals(destinationUserId)) {
            throw new BadRequestException("Source and destination users must be different");
        }

        // Fetch both users
        UserRepository.User sourceUser = userRepository.findById(sourceUserId)
            .orElseThrow(() -> new NotFoundException("Source user not found: " + sourceUserId));

        UserRepository.User destinationUser = userRepository.findById(destinationUserId)
            .orElseThrow(() -> new NotFoundException("Destination user not found: " + destinationUserId));

        // Check for overlapping identities
        java.util.List<String> conflicts = new java.util.ArrayList<>();

        // Check local identity overlap
        boolean sourceHasLocal = sourceUser.localEnabled() && sourceUser.localUsername() != null;
        boolean destHasLocal = destinationUser.localEnabled() && destinationUser.localUsername() != null;
        if (sourceHasLocal && destHasLocal) {
            conflicts.add("local");
        }

        // Check Google identity overlap
        boolean sourceHasGoogle = sourceUser.googleSub() != null;
        boolean destHasGoogle = destinationUser.googleSub() != null;
        if (sourceHasGoogle && destHasGoogle) {
            conflicts.add("google");
        }

        // Check Microsoft identity overlap
        boolean sourceHasMicrosoft = sourceUser.msOid() != null && sourceUser.msTid() != null;
        boolean destHasMicrosoft = destinationUser.msOid() != null && destinationUser.msTid() != null;
        if (sourceHasMicrosoft && destHasMicrosoft) {
            conflicts.add("microsoft");
        }

        // If there are overlapping identities, fail the merge
        if (!conflicts.isEmpty()) {
            throw new BadRequestException(
                "Cannot merge accounts - overlapping identities: " + String.join(", ", conflicts) +
                ". Both users have the following identity types linked."
            );
        }

        // Prepare merged identities tracking
        java.util.Map<String, Boolean> mergedIdentities = new java.util.HashMap<>();

        // Build updated destination user with merged identities
        String newLocalUsername = destHasLocal ? destinationUser.localUsername() :
            (sourceHasLocal ? sourceUser.localUsername() : destinationUser.localUsername());
        String newLocalPasswordHash = destHasLocal ? destinationUser.localPasswordHash() :
            (sourceHasLocal ? sourceUser.localPasswordHash() : destinationUser.localPasswordHash());
        Boolean newLocalEnabled = destHasLocal ? destinationUser.localEnabled() :
            (sourceHasLocal ? sourceUser.localEnabled() : destinationUser.localEnabled());

        String newGoogleSub = destHasGoogle ? destinationUser.googleSub() :
            (sourceHasGoogle ? sourceUser.googleSub() : destinationUser.googleSub());
        String newGoogleEmail = destHasGoogle ? destinationUser.googleEmail() :
            (sourceHasGoogle ? sourceUser.googleEmail() : destinationUser.googleEmail());

        UUID newMsOid = destHasMicrosoft ? destinationUser.msOid() :
            (sourceHasMicrosoft ? sourceUser.msOid() : destinationUser.msOid());
        UUID newMsTid = destHasMicrosoft ? destinationUser.msTid() :
            (sourceHasMicrosoft ? sourceUser.msTid() : destinationUser.msTid());
        String newMsEmail = destHasMicrosoft ? destinationUser.msEmail() :
            (sourceHasMicrosoft ? sourceUser.msEmail() : destinationUser.msEmail());

        if (sourceHasLocal && !destHasLocal) {
            mergedIdentities.put("local", true);
        }
        if (sourceHasGoogle && !destHasGoogle) {
            mergedIdentities.put("google", true);
        }
        if (sourceHasMicrosoft && !destHasMicrosoft) {
            mergedIdentities.put("microsoft", true);
        }

        // If destination email is not verified but source is, update verification
        var newEmailVerifiedAt = destinationUser.emailVerifiedAt() != null ?
            destinationUser.emailVerifiedAt() :
            (sourceUser.emailVerifiedAt() != null ? sourceUser.emailVerifiedAt() : null);

        // Create updated destination user
        UserRepository.User updatedDestination = new UserRepository.User(
            destinationUser.id(),
            destinationUser.email(), // Will be recomputed
            destinationUser.fullName(),
            destinationUser.role(),
            newEmailVerifiedAt,
            newLocalUsername,
            newLocalPasswordHash,
            newLocalEnabled,
            newGoogleSub,
            newGoogleEmail,
            newMsOid,
            newMsTid,
            newMsEmail,
            destinationUser.createdAt(),
            destinationUser.updatedAt()
        );

        // Save changes
        userRepository.update(updatedDestination);

        // Delete the source user
        userRepository.deleteById(sourceUserId);

        // Log the merge operation
        try {
            String metadata = String.format(
                "{\"sourceUserId\":\"%s\",\"destinationUserId\":\"%s\",\"mergedIdentities\":%s,\"sourceUserEmail\":\"%s\",\"destinationUserEmail\":\"%s\"}",
                sourceUserId, destinationUserId,
                new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(mergedIdentities),
                sourceUser.email(), destinationUser.email()
            );
            auditService.logAction(destinationUserId, "ACCOUNTS_MERGED", metadata, ipAddress, userAgent);
        } catch (Exception e) {
            log.error("Failed to log merge operation", e);
        }

        log.info("Merged user {} into user {}", sourceUserId, destinationUserId);

        return java.util.Map.of(
            "destinationUserId", destinationUserId,
            "mergedIdentities", mergedIdentities
        );
    }
}
