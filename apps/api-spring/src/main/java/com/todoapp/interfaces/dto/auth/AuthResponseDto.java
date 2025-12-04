package com.todoapp.interfaces.dto.auth;

import com.todoapp.interfaces.dto.user.UserInfoDto;

public record AuthResponseDto(
    String accessToken,
    String refreshToken,
    UserInfoDto user
) {}
