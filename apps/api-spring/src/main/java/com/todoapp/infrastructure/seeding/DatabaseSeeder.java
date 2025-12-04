package com.todoapp.infrastructure.seeding;

import com.todoapp.domain.model.Priority;
import com.todoapp.domain.model.Role;
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
            Role.SYSADMIN
        );
        userRepository.markEmailVerified(sysadminId);
        log.info("Created sysadmin: admin@example.com");

        // Create regular admin
        String adminPassword = passwordEncoder.encode("Admin123!");
        UUID adminId = userRepository.createUser(
            "moderator@example.com",
            adminPassword,
            "Moderator Admin",
            Role.ADMIN
        );
        userRepository.markEmailVerified(adminId);
        log.info("Created admin: moderator@example.com");

        // Create regular users
        String userPassword = passwordEncoder.encode("User123!");
        
        UUID user1Id = userRepository.createUser(
            "alice@example.com",
            userPassword,
            "Alice Johnson",
            Role.USER
        );
        userRepository.markEmailVerified(user1Id);
        log.info("Created user: alice@example.com");

        UUID user2Id = userRepository.createUser(
            "bob@example.com",
            userPassword,
            "Bob Smith",
            Role.USER
        );
        userRepository.markEmailVerified(user2Id);
        log.info("Created user: bob@example.com");

        UUID user3Id = userRepository.createUser(
            "charlie@example.com",
            userPassword,
            "Charlie Brown",
            Role.USER
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
            "Complete project documentation",
            "Write comprehensive documentation for the Spring Boot project",
            Priority.HIGH,
            Instant.now().plus(7, ChronoUnit.DAYS)
        );

        UUID aliceTodo2 = todoRepository.createTodo(
            aliceId,
            "Review pull requests",
            "Review and merge pending pull requests",
            Priority.MEDIUM,
            Instant.now().plus(2, ChronoUnit.DAYS)
        );
        
        // Mark one as completed
        var completedTodo = todoRepository.findById(aliceTodo2).orElseThrow();
        todoRepository.update(new TodoRepository.Todo(
            completedTodo.id(),
            completedTodo.ownerId(),
            completedTodo.title(),
            completedTodo.description(),
            completedTodo.priority(),
            true, // completed
            completedTodo.dueDate(),
            completedTodo.createdAt(),
            completedTodo.updatedAt()
        ));

        todoRepository.createTodo(
            aliceId,
            "Update dependencies",
            "Update all project dependencies to latest versions",
            Priority.LOW,
            Instant.now().plus(14, ChronoUnit.DAYS)
        );

        // Bob's todos
        todoRepository.createTodo(
            bobId,
            "Fix authentication bug",
            "Investigate and fix the JWT token refresh issue",
            Priority.HIGH,
            Instant.now().plus(1, ChronoUnit.DAYS)
        );

        todoRepository.createTodo(
            bobId,
            "Write unit tests",
            "Add unit tests for the todo service layer",
            Priority.MEDIUM,
            Instant.now().plus(5, ChronoUnit.DAYS)
        );

        todoRepository.createTodo(
            bobId,
            "Database optimization",
            "Optimize database queries and add indexes",
            Priority.MEDIUM,
            null // No due date
        );

        todoRepository.createTodo(
            bobId,
            "Setup CI/CD pipeline",
            "Configure GitHub Actions for automated testing and deployment",
            Priority.LOW,
            Instant.now().plus(30, ChronoUnit.DAYS)
        );

        log.info("Seeded {} todos", 7);
    }
}
