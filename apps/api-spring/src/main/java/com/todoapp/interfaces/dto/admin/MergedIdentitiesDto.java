package com.todoapp.interfaces.dto.admin;

public record MergedIdentitiesDto(
    Boolean local,
    Boolean google,
    Boolean microsoft
) {}
