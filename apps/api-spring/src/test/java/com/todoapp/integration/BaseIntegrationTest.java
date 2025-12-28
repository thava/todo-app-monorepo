package com.todoapp.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.jooq.DSLContext;

import static com.todoapp.infrastructure.jooq.tables.AuditLogs.AUDIT_LOGS;
import static com.todoapp.infrastructure.jooq.tables.EmailVerificationTokens.EMAIL_VERIFICATION_TOKENS;
import static com.todoapp.infrastructure.jooq.tables.PasswordResetTokens.PASSWORD_RESET_TOKENS;
import static com.todoapp.infrastructure.jooq.tables.RefreshTokenSessions.REFRESH_TOKEN_SESSIONS;
import static com.todoapp.infrastructure.jooq.tables.Todos.TODOS;
import static com.todoapp.infrastructure.jooq.tables.Users.USERS;

/**
 * Base class for integration tests
 * Provides common test infrastructure and database cleanup
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestPropertySource(locations = "classpath:application-test.properties")
public abstract class BaseIntegrationTest {

    @Autowired
    protected MockMvc mockMvc;

    @Autowired
    protected ObjectMapper objectMapper;

    @Autowired
    private DSLContext dsl;

    @BeforeEach
    void cleanDatabase() {
        // Clean all tables before each test to ensure isolation
        // Order matters due to foreign key constraints
        dsl.deleteFrom(AUDIT_LOGS).execute();
        dsl.deleteFrom(TODOS).execute();
        dsl.deleteFrom(EMAIL_VERIFICATION_TOKENS).execute();
        dsl.deleteFrom(PASSWORD_RESET_TOKENS).execute();
        dsl.deleteFrom(REFRESH_TOKEN_SESSIONS).execute();
        dsl.deleteFrom(USERS).execute();
    }

    /**
     * Helper method to serialize objects to JSON
     */
    protected String toJson(Object object) throws Exception {
        return objectMapper.writeValueAsString(object);
    }

    /**
     * Helper method to deserialize JSON to objects
     */
    protected <T> T fromJson(String json, Class<T> clazz) throws Exception {
        return objectMapper.readValue(json, clazz);
    }
}
