package com.todoapp.integration;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for authentication flows
 * Tests the complete user journey: register → login → refresh → logout
 */
class AuthFlowIntegrationTest extends BaseIntegrationTest {

    @Test
    void shouldRegisterNewUser() throws Exception {
        // Given
        String email = "newuser@example.com";
        String password = "Password123";
        String fullName = "New User";

        String requestBody = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\",\"fullName\":\"%s\",\"autoverify\":true}",
            email, password, fullName
        );

        // When & Then
        mockMvc.perform(post("/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.user.email").value(email))
            .andExpect(jsonPath("$.user.fullName").value(fullName))
            .andExpect(jsonPath("$.user.role").value("guest"))
            .andExpect(jsonPath("$.user.emailVerified").value(true))
            .andExpect(jsonPath("$.accessToken").exists())
            .andExpect(jsonPath("$.refreshToken").exists());
    }

    @Test
    void shouldNotRegisterUserWithDuplicateEmail() throws Exception {
        // Given
        String email = "duplicate@example.com";
        String password = "Password123";

        String requestBody = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\",\"fullName\":\"User\"}",
            email, password
        );

        // Register first user
        mockMvc.perform(post("/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isCreated());

        // When & Then - Try to register again
        mockMvc.perform(post("/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.title").value("Bad Request"));
    }

    @Test
    void shouldLoginWithValidCredentials() throws Exception {
        // Given
        String email = "logintest@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        authHelper.registerGuestUser(email, password);

        String loginRequest = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\"}",
            email, password
        );

        // When & Then
        mockMvc.perform(post("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(loginRequest))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.user.email").value(email))
            .andExpect(jsonPath("$.accessToken").exists())
            .andExpect(jsonPath("$.refreshToken").exists());
    }

    @Test
    void shouldNotLoginWithInvalidPassword() throws Exception {
        // Given
        String email = "badpassword@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        authHelper.registerGuestUser(email, password);

        String loginRequest = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\"}",
            email, "WrongPassword"
        );

        // When & Then
        mockMvc.perform(post("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(loginRequest))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldRefreshAccessToken() throws Exception {
        // Given
        String email = "refreshtest@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        authHelper.registerGuestUser(email, password);
        String refreshToken = authHelper.loginAndGetRefreshToken(email, password);

        String refreshRequest = String.format("{\"refreshToken\":\"%s\"}", refreshToken);

        // When & Then
        mockMvc.perform(post("/auth/refresh")
                .contentType(MediaType.APPLICATION_JSON)
                .content(refreshRequest))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.accessToken").exists())
            .andExpect(jsonPath("$.refreshToken").exists())
            .andExpect(jsonPath("$.refreshToken").value(org.hamcrest.Matchers.not(refreshToken))); // Token should rotate
    }

    @Test
    void shouldLogoutAndRevokeRefreshToken() throws Exception {
        // Given
        String email = "logouttest@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        authHelper.registerGuestUser(email, password);
        String refreshToken = authHelper.loginAndGetRefreshToken(email, password);

        String logoutRequest = String.format("{\"refreshToken\":\"%s\"}", refreshToken);

        // When - Logout
        mockMvc.perform(post("/auth/logout")
                .contentType(MediaType.APPLICATION_JSON)
                .content(logoutRequest))
            .andExpect(status().isNoContent());

        // Then - Try to refresh with revoked token
        String refreshRequest = String.format("{\"refreshToken\":\"%s\"}", refreshToken);

        mockMvc.perform(post("/auth/refresh")
                .contentType(MediaType.APPLICATION_JSON)
                .content(refreshRequest))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldAccessProtectedEndpointWithValidToken() throws Exception {
        // Given
        String email = "protected@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        String accessToken = authHelper.registerAndLoginGuest(email, password);

        // When & Then
        mockMvc.perform(get("/me")
                .header("Authorization", "Bearer " + accessToken))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value(email));
    }

    @Test
    void shouldNotAccessProtectedEndpointWithoutToken() throws Exception {
        // When & Then
        mockMvc.perform(get("/me"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldNotAccessProtectedEndpointWithInvalidToken() throws Exception {
        // When & Then
        mockMvc.perform(get("/me")
                .header("Authorization", "Bearer invalid-token"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldRegisterUsersWithDifferentRoles() throws Exception {
        // Given
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        // When & Then - Register guest
        MvcResult guestResult = authHelper.registerGuestUser("guest@example.com", "Password123");
        String guestResponse = guestResult.getResponse().getContentAsString();
        JsonNode guestNode = objectMapper.readTree(guestResponse);
        assertThat(guestNode.get("user").get("role").asText()).isEqualTo("guest");

        // When & Then - Register admin
        MvcResult adminResult = authHelper.registerAdminUser("admin@example.com", "Password123");
        String adminResponse = adminResult.getResponse().getContentAsString();
        JsonNode adminNode = objectMapper.readTree(adminResponse);
        assertThat(adminNode.get("user").get("role").asText()).isEqualTo("admin");

        // When & Then - Register sysadmin
        MvcResult sysadminResult = authHelper.registerSysadminUser("sysadmin@example.com", "Password123");
        String sysadminResponse = sysadminResult.getResponse().getContentAsString();
        JsonNode sysadminNode = objectMapper.readTree(sysadminResponse);
        assertThat(sysadminNode.get("user").get("role").asText()).isEqualTo("sysadmin");
    }

    @Test
    void shouldUpdateUserProfile() throws Exception {
        // Given
        String email = "profile@example.com";
        String password = "Password123";
        TestAuthHelper authHelper = new TestAuthHelper(mockMvc, objectMapper);

        String accessToken = authHelper.registerAndLoginGuest(email, password);

        String updateRequest = "{\"fullName\":\"Updated Name\"}";

        // When & Then
        mockMvc.perform(patch("/me")
                .header("Authorization", "Bearer " + accessToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(updateRequest))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.fullName").value("Updated Name"));
    }
}
