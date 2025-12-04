package com.todoapp.integration;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for Todo CRUD operations with authorization
 * Tests complete todo lifecycle and authorization rules
 */
class TodoCrudIntegrationTest extends BaseIntegrationTest {

    @Test
    void shouldCreateTodo() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String accessToken = authHelper.registerAndLoginGuest("user@example.com", "Password123");

        Instant dueDate = Instant.now().plus(7, ChronoUnit.DAYS);
        String requestBody = String.format(
            "{\"description\":\"Buy groceries\",\"priority\":\"high\",\"dueDate\":\"%s\"}",
            dueDate.toString()
        );

        // When & Then
        mockMvc.perform(post("/todos")
                .header("Authorization", "Bearer " + accessToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.description").value("Buy groceries"))
            .andExpect(jsonPath("$.priority").value("high"))
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.ownerId").exists());
    }

    @Test
    void shouldListOwnTodosAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String user1Token = authHelper.registerAndLoginGuest("user1@example.com", "Password123");
        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        // Create todos for user1
        createTodo(user1Token, "User1 Todo 1", "high");
        createTodo(user1Token, "User1 Todo 2", "medium");

        // Create todo for user2
        createTodo(user2Token, "User2 Todo", "low");

        // When & Then - User1 should only see their todos
        MvcResult result = mockMvc.perform(get("/todos")
                .header("Authorization", "Bearer " + user1Token))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);

        assertThat(jsonNode).isArray();
        assertThat(jsonNode).hasSize(2);
        assertThat(jsonNode.get(0).get("description").asText()).contains("User1");
        assertThat(jsonNode.get(1).get("description").asText()).contains("User1");
    }

    @Test
    void shouldListAllTodosAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String guestToken = authHelper.registerAndLoginGuest("guest@example.com", "Password123");
        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        // Create todos as guest
        createTodo(guestToken, "Guest Todo 1", "high");
        createTodo(guestToken, "Guest Todo 2", "medium");

        // When & Then - Admin should see all todos
        MvcResult result = mockMvc.perform(get("/todos")
                .header("Authorization", "Bearer " + adminToken))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);

        assertThat(jsonNode).isArray();
        assertThat(jsonNode.size()).isGreaterThanOrEqualTo(2);
    }

    @Test
    void shouldGetTodoById() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String accessToken = authHelper.registerAndLoginGuest("user@example.com", "Password123");

        String todoId = createTodo(accessToken, "Test Todo", "medium");

        // When & Then
        mockMvc.perform(get("/todos/" + todoId)
                .header("Authorization", "Bearer " + accessToken))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(todoId))
            .andExpect(jsonPath("$.description").value("Test Todo"))
            .andExpect(jsonPath("$.priority").value("medium"));
    }

    @Test
    void shouldNotGetOtherUsersTodoAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String user1Token = authHelper.registerAndLoginGuest("user1@example.com", "Password123");
        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        String user1TodoId = createTodo(user1Token, "User1 Todo", "high");

        // When & Then - User2 tries to access User1's todo
        mockMvc.perform(get("/todos/" + user1TodoId)
                .header("Authorization", "Bearer " + user2Token))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldGetOtherUsersTodoAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String guestToken = authHelper.registerAndLoginGuest("guest@example.com", "Password123");
        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        String guestTodoId = createTodo(guestToken, "Guest Todo", "high");

        // When & Then - Admin can access guest's todo
        mockMvc.perform(get("/todos/" + guestTodoId)
                .header("Authorization", "Bearer " + adminToken))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.description").value("Guest Todo"));
    }

    @Test
    void shouldUpdateOwnTodo() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String accessToken = authHelper.registerAndLoginGuest("user@example.com", "Password123");

        String todoId = createTodo(accessToken, "Original Description", "low");

        String updateRequest = "{\"description\":\"Updated Description\",\"priority\":\"high\"}";

        // When & Then
        mockMvc.perform(patch("/todos/" + todoId)
                .header("Authorization", "Bearer " + accessToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.description").value("Updated Description"))
            .andExpect(jsonPath("$.priority").value("high"));
    }

    @Test
    void shouldNotUpdateOtherUsersTodo() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String user1Token = authHelper.registerAndLoginGuest("user1@example.com", "Password123");
        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        String user1TodoId = createTodo(user1Token, "User1 Todo", "low");

        String updateRequest = "{\"description\":\"Hacked\"}";

        // When & Then - User2 tries to update User1's todo
        mockMvc.perform(patch("/todos/" + user1TodoId)
                .header("Authorization", "Bearer " + user2Token)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldNotUpdateOtherUsersTodoEvenAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String guestToken = authHelper.registerAndLoginGuest("guest@example.com", "Password123");
        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        String guestTodoId = createTodo(guestToken, "Guest Todo", "low");

        String updateRequest = "{\"description\":\"Admin Update\"}";

        // When & Then - Admin cannot update guest's todo (only owners can update)
        mockMvc.perform(patch("/todos/" + guestTodoId)
                .header("Authorization", "Bearer " + adminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldDeleteOwnTodo() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String accessToken = authHelper.registerAndLoginGuest("user@example.com", "Password123");

        String todoId = createTodo(accessToken, "To Delete", "low");

        // When & Then
        mockMvc.perform(delete("/todos/" + todoId)
                .header("Authorization", "Bearer " + accessToken))
            .andExpect(status().isNoContent());

        // Verify todo is deleted
        mockMvc.perform(get("/todos/" + todoId)
                .header("Authorization", "Bearer " + accessToken))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldNotDeleteOtherUsersTodo() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String user1Token = authHelper.registerAndLoginGuest("user1@example.com", "Password123");
        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        String user1TodoId = createTodo(user1Token, "User1 Todo", "low");

        // When & Then - User2 tries to delete User1's todo
        mockMvc.perform(delete("/todos/" + user1TodoId)
                .header("Authorization", "Bearer " + user2Token))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldNotAccessTodosWithoutAuthentication() throws Exception {
        // When & Then
        mockMvc.perform(get("/todos"))
            .andExpect(status().isUnauthorized());

        mockMvc.perform(post("/todos")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"description\":\"Test\"}"))
            .andExpect(status().isUnauthorized());
    }

    /**
     * Helper method to create a todo and return its ID
     */
    private String createTodo(String accessToken, String description, String priority) throws Exception {
        String requestBody = String.format(
            "{\"description\":\"%s\",\"priority\":\"%s\"}",
            description, priority
        );

        MvcResult result = mockMvc.perform(post("/todos")
                .header("Authorization", "Bearer " + accessToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isCreated())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);
        return jsonNode.get("id").asText();
    }
}
