package com.todoapp.domain.exception;

/**
 * Exception thrown when user lacks permission for a resource
 */
public class ForbiddenException extends RuntimeException {
    public ForbiddenException(String message) {
        super(message);
    }
}
