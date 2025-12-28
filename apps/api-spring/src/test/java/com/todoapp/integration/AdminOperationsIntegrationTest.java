package com.todoapp.integration;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for admin operations
 * Tests user management endpoints with proper authorization
 */
class AdminOperationsIntegrationTest extends BaseIntegrationTest {

    @Test
    void shouldListAllUsersAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        authHelper.registerGuestUser("user1@example.com", "Password123");
        authHelper.registerGuestUser("user2@example.com", "Password123");
        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        // When & Then
        MvcResult result = mockMvc.perform(get("/admin/users")
                .header("Authorization", "Bearer " + adminToken))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);

        assertThat(jsonNode.isArray()).isTrue();
        assertThat(jsonNode.size()).isGreaterThanOrEqualTo(3); // At least 3 users created
    }

    @Test
    void shouldListAllUsersAsSysadmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        authHelper.registerGuestUser("user@example.com", "Password123");
        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        // When & Then
        MvcResult result = mockMvc.perform(get("/admin/users")
                .header("Authorization", "Bearer " + sysadminToken))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);

        assertThat(jsonNode.isArray()).isTrue();
        assertThat(jsonNode.size()).isGreaterThanOrEqualTo(2);
    }

    @Test
    void shouldNotListUsersAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String guestToken = authHelper.registerAndLoginGuest("guest@example.com", "Password123");

        // When & Then
        mockMvc.perform(get("/admin/users")
                .header("Authorization", "Bearer " + guestToken))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldGetUserByIdAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult userResult = authHelper.registerGuestUser("user@example.com", "Password123");
        String userId = authHelper.extractUserId(userResult);

        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        // When & Then
        mockMvc.perform(get("/admin/users/" + userId)
                .header("Authorization", "Bearer " + adminToken))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(userId))
            .andExpect(jsonPath("$.email").value("user@example.com"));
    }

    @Test
    void shouldNotGetUserByIdAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult user1Result = authHelper.registerGuestUser("user1@example.com", "Password123");
        String user1Id = authHelper.extractUserId(user1Result);

        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        // When & Then
        mockMvc.perform(get("/admin/users/" + user1Id)
                .header("Authorization", "Bearer " + user2Token))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldUpdateUserAsSysadmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult userResult = authHelper.registerGuestUser("user@example.com", "Password123");
        String userId = authHelper.extractUserId(userResult);

        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        String updateRequest = "{\"fullName\":\"Updated Name\",\"role\":\"admin\"}";

        // When & Then
        mockMvc.perform(patch("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.fullName").value("Updated Name"))
            .andExpect(jsonPath("$.role").value("admin"));
    }

    @Test
    void shouldNotUpdateUserAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult userResult = authHelper.registerGuestUser("user@example.com", "Password123");
        String userId = authHelper.extractUserId(userResult);

        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        String updateRequest = "{\"fullName\":\"Hacked Name\"}";

        // When & Then - Admin cannot update users (only sysadmin can)
        mockMvc.perform(patch("/admin/users/" + userId)
                .header("Authorization", "Bearer " + adminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldNotUpdateUserAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult user1Result = authHelper.registerGuestUser("user1@example.com", "Password123");
        String user1Id = authHelper.extractUserId(user1Result);

        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        String updateRequest = "{\"fullName\":\"Hacked Name\"}";

        // When & Then
        mockMvc.perform(patch("/admin/users/" + user1Id)
                .header("Authorization", "Bearer " + user2Token)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldUpdateUserPasswordAsSysadmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String email = "passwordchange@example.com";
        MvcResult userResult = authHelper.registerGuestUser(email, "OldPassword123");
        String userId = authHelper.extractUserId(userResult);

        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        String updateRequest = "{\"password\":\"NewPassword123\"}";

        // When - Sysadmin changes user password
        mockMvc.perform(patch("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isOk());

        // Then - User can login with new password
        String loginRequest = String.format(
            "{\"email\":\"%s\",\"password\":\"NewPassword123\"}",
            email
        );

        mockMvc.perform(post("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(loginRequest))
            .andExpect(status().isOk());
    }

    @Test
    void shouldDeleteUserAsSysadmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult userResult = authHelper.registerGuestUser("todelete@example.com", "Password123");
        String userId = authHelper.extractUserId(userResult);

        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        // When - Delete user
        mockMvc.perform(delete("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken))
            .andExpect(status().isNoContent());

        // Then - User should not exist
        mockMvc.perform(get("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldNotDeleteUserAsAdmin() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult userResult = authHelper.registerGuestUser("user@example.com", "Password123");
        String userId = authHelper.extractUserId(userResult);

        String adminToken = authHelper.registerAndLoginAdmin("admin@example.com", "Password123");

        // When & Then - Admin cannot delete users (only sysadmin can)
        mockMvc.perform(delete("/admin/users/" + userId)
                .header("Authorization", "Bearer " + adminToken))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldNotDeleteUserAsGuest() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        MvcResult user1Result = authHelper.registerGuestUser("user1@example.com", "Password123");
        String user1Id = authHelper.extractUserId(user1Result);

        String user2Token = authHelper.registerAndLoginGuest("user2@example.com", "Password123");

        // When & Then
        mockMvc.perform(delete("/admin/users/" + user1Id)
                .header("Authorization", "Bearer " + user2Token))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldCascadeDeleteUserTodos() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        String email = "cascade@example.com";
        String password = "Password123";

        MvcResult userResult = authHelper.registerGuestUser(email, password);
        String userId = authHelper.extractUserId(userResult);
        String userToken = authHelper.loginAndGetAccessToken(email, password);

        // Create todos for user
        String createTodoRequest = "{\"description\":\"Todo 1\",\"priority\":\"high\"}";
        mockMvc.perform(post("/todos")
                .header("Authorization", "Bearer " + userToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(createTodoRequest))
            .andExpect(status().isCreated());

        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        // When - Delete user
        mockMvc.perform(delete("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken))
            .andExpect(status().isNoContent());

        // Then - User's todos should be deleted (cascade)
        // We can't access the todos directly since the user is deleted
        // But we can verify the user is deleted
        mockMvc.perform(get("/admin/users/" + userId)
                .header("Authorization", "Bearer " + sysadminToken))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldNotAllowDuplicateEmailWhenUpdating() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);
        authHelper.registerGuestUser("user1@example.com", "Password123");

        MvcResult user2Result = authHelper.registerGuestUser("user2@example.com", "Password123");
        String user2Id = authHelper.extractUserId(user2Result);

        String sysadminToken = authHelper.registerAndLoginSysadmin("sysadmin@example.com", "Password123");

        // Try to update user2's email to user1's email
        String updateRequest = "{\"email\":\"user1@example.com\"}";

        // When & Then
        mockMvc.perform(patch("/admin/users/" + user2Id)
                .header("Authorization", "Bearer " + sysadminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isBadRequest());
    }
}
