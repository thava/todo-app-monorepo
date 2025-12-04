package com.todoapp.domain.model;

/**
 * User role enumeration
 * Maps to database ENUM type
 */
public enum Role {
    GUEST("guest"),
    ADMIN("admin"),
    SYSADMIN("sysadmin");

    private final String value;

    Role(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public static Role fromValue(String value) {
        for (Role role : Role.values()) {
            if (role.value.equalsIgnoreCase(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Invalid role: " + value);
    }
}
