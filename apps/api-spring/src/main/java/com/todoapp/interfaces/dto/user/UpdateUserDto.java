package com.todoapp.interfaces.dto.user;

import com.todoapp.domain.model.Role;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record UpdateUserDto(
    @Email(message = "Invalid email format")
    String email,
    
    @Size(min = 8, message = "Password must be at least 8 characters")
    String password,
    
    @Size(min = 2, max = 100, message = "Full name must be between 2 and 100 characters")
    String fullName,
    
    Role role,
    
    Boolean emailVerified
) {}
