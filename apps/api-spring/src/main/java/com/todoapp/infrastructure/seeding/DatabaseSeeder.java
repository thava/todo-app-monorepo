package com.todoapp.infrastructure.seeding;

import com.todoapp.infrastructure.jooq.enums.Priority;
import com.todoapp.infrastructure.jooq.enums.Role;
import com.todoapp.domain.repository.TodoRepository;
import com.todoapp.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

@Slf4j
@Component
@RequiredArgsConstructor
public class DatabaseSeeder implements CommandLineRunner {

    private final UserRepository userRepository;
    private final TodoRepository todoRepository;
    private final PasswordEncoder passwordEncoder;
    private final SeedingConfig seedingConfig;

    @Override
    public void run(String... args) {
        if (!seedingConfig.isEnabled()) {
            log.info("Database seeding is disabled");
            return;
        }

        log.info("Starting database seeding...");
        
        try {
            // Check if already seeded
            if (userRepository.existsByEmail("admin@example.com")) {
                log.info("Database already seeded, skipping...");
                return;
            }

            seedUsers();
            seedTodos();
            
            log.info("Database seeding completed successfully!");
        } catch (Exception e) {
            log.error("Error seeding database", e);
            // Don't throw - allow application to start even if seeding fails
        }
    }

    private void seedUsers() {
        log.info("Seeding users...");
        
        // Create sysadmin
        String sysadminPassword = passwordEncoder.encode("Admin123!");
        UUID sysadminId = userRepository.createUser(
            "admin@example.com",
            sysadminPassword,
            "System Administrator",
            Role.sysadmin
        );
        userRepository.markEmailVerified(sysadminId);
        log.info("Created sysadmin: admin@example.com");

        // Create regular admin
        String adminPassword = passwordEncoder.encode("Admin123!");
        UUID adminId = userRepository.createUser(
            "moderator@example.com",
            adminPassword,
            "Moderator Admin",
            Role.admin
        );
        userRepository.markEmailVerified(adminId);
        log.info("Created admin: moderator@example.com");

        // Create regular users
        String userPassword = passwordEncoder.encode("User123!");
        
        UUID user1Id = userRepository.createUser(
            "alice@example.com",
            userPassword,
            "Alice Johnson",
            Role.guest
        );
        userRepository.markEmailVerified(user1Id);
        log.info("Created user: alice@example.com");

        UUID user2Id = userRepository.createUser(
            "bob@example.com",
            userPassword,
            "Bob Smith",
            Role.guest
        );
        userRepository.markEmailVerified(user2Id);
        log.info("Created user: bob@example.com");

        UUID user3Id = userRepository.createUser(
            "charlie@example.com",
            userPassword,
            "Charlie Brown",
            Role.guest
        );
        // Don't verify charlie's email
        log.info("Created user: charlie@example.com (unverified)");

        log.info("Seeded {} users", 5);
    }

    private void seedTodos() {
        log.info("Seeding todos...");
        
        // Get Alice's ID
        UUID aliceId = userRepository.findByEmail("alice@example.com")
            .map(UserRepository.User::id)
            .orElseThrow();

        // Get Bob's ID
        UUID bobId = userRepository.findByEmail("bob@example.com")
            .map(UserRepository.User::id)
            .orElseThrow();

        // Alice's todos
        todoRepository.createTodo(
            aliceId,
            "Write comprehensive documentation for the Spring Boot project",
            false,
            Priority.high,
            Instant.now().plus(7, ChronoUnit.DAYS)
        );

        UUID aliceTodo2 = todoRepository.createTodo(
            aliceId,
            "Review and merge pending pull requests",
            false,
            Priority.medium,
            Instant.now().plus(2, ChronoUnit.DAYS)
        );

        // Mark one as completed
        var completedTodo = todoRepository.findById(aliceTodo2).orElseThrow();
        todoRepository.update(new TodoRepository.Todo(
            completedTodo.id(),
            completedTodo.ownerId(),
            completedTodo.description(),
            true, // completed
            completedTodo.priority(),
            completedTodo.dueDate(),
            completedTodo.createdAt(),
            completedTodo.updatedAt()
        ));

        todoRepository.createTodo(
            aliceId,
            "Update all project dependencies to latest versions",
            false,
            Priority.low,
            Instant.now().plus(14, ChronoUnit.DAYS)
        );

        // Bob's todos
        todoRepository.createTodo(
            bobId,
            "Investigate and fix the JWT token refresh issue",
            false,
            Priority.high,
            Instant.now().plus(1, ChronoUnit.DAYS)
        );

        todoRepository.createTodo(
            bobId,
            "Add unit tests for the todo service layer",
            false,
            Priority.medium,
            Instant.now().plus(5, ChronoUnit.DAYS)
        );

        todoRepository.createTodo(
            bobId,
            "Optimize database queries and add indexes",
            false,
            Priority.medium,
            null // No due date
        );

        todoRepository.createTodo(
            bobId,
            "Configure GitHub Actions for automated testing and deployment",
            false,
            Priority.low,
            Instant.now().plus(30, ChronoUnit.DAYS)
        );

        log.info("Seeded {} todos", 7);
    }
}
