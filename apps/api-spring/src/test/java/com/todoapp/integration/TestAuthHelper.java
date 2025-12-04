package com.todoapp.integration;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Helper class for authentication operations in integration tests
 */
public class TestAuthHelper {

    private final MockMvc mockMvc;
    private final ObjectMapper objectMapper;

    public TestAuthHelper(MockMvc mockMvc, ObjectMapper objectMapper) {
        this.mockMvc = mockMvc;
        this.objectMapper = objectMapper;
    }

    /**
     * Register a new user and return the response
     */
    public MvcResult registerUser(String email, String password, String fullName, String role) throws Exception {
        String requestBody = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\",\"fullName\":\"%s\",\"role\":\"%s\",\"autoverify\":true}",
            email, password, fullName, role
        );

        return mockMvc.perform(post("/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isCreated())
            .andReturn();
    }

    /**
     * Register a guest user with default values
     */
    public MvcResult registerGuestUser(String email, String password) throws Exception {
        return registerUser(email, password, "Test User", "guest");
    }

    /**
     * Register an admin user
     */
    public MvcResult registerAdminUser(String email, String password) throws Exception {
        return registerUser(email, password, "Admin User", "admin");
    }

    /**
     * Register a sysadmin user
     */
    public MvcResult registerSysadminUser(String email, String password) throws Exception {
        return registerUser(email, password, "Sysadmin User", "sysadmin");
    }

    /**
     * Login and return the access token
     */
    public String loginAndGetAccessToken(String email, String password) throws Exception {
        String requestBody = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\"}",
            email, password
        );

        MvcResult result = mockMvc.perform(post("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);
        return jsonNode.get("accessToken").asText();
    }

    /**
     * Login and return the refresh token
     */
    public String loginAndGetRefreshToken(String email, String password) throws Exception {
        String requestBody = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\"}",
            email, password
        );

        MvcResult result = mockMvc.perform(post("/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isOk())
            .andReturn();

        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);
        return jsonNode.get("refreshToken").asText();
    }

    /**
     * Register and login a guest user, return access token
     */
    public String registerAndLoginGuest(String email, String password) throws Exception {
        registerGuestUser(email, password);
        return loginAndGetAccessToken(email, password);
    }

    /**
     * Register and login an admin user, return access token
     */
    public String registerAndLoginAdmin(String email, String password) throws Exception {
        registerAdminUser(email, password);
        return loginAndGetAccessToken(email, password);
    }

    /**
     * Register and login a sysadmin user, return access token
     */
    public String registerAndLoginSysadmin(String email, String password) throws Exception {
        registerSysadminUser(email, password);
        return loginAndGetAccessToken(email, password);
    }

    /**
     * Logout using refresh token
     */
    public void logout(String refreshToken) throws Exception {
        String requestBody = String.format("{\"refreshToken\":\"%s\"}", refreshToken);

        mockMvc.perform(post("/auth/logout")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isNoContent());
    }

    /**
     * Extract user ID from JWT response
     */
    public String extractUserId(MvcResult result) throws Exception {
        String responseBody = result.getResponse().getContentAsString();
        JsonNode jsonNode = objectMapper.readTree(responseBody);
        return jsonNode.get("user").get("id").asText();
    }
}
