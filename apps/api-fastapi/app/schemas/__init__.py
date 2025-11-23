"""API schemas (DTOs) for request/response validation."""

from app.schemas.auth import (
    AuthResponseDto,
    LoginDto,
    RefreshTokenDto,
    RegisterDto,
    RegisteredUserInfo,
    RegisterResponseDto,
    RequestPasswordResetDto,
    ResetPasswordDto,
    UserInfo,
)
from app.schemas.base import CamelCaseModel, to_camel
from app.schemas.todo import CreateTodoDto, TodoResponseDto, UpdateTodoDto

__all__ = [
    # Base
    "CamelCaseModel",
    "to_camel",
    # Auth
    "RegisterDto",
    "RegisteredUserInfo",
    "RegisterResponseDto",
    "LoginDto",
    "UserInfo",
    "AuthResponseDto",
    "RefreshTokenDto",
    "RequestPasswordResetDto",
    "ResetPasswordDto",
    # Todo
    "CreateTodoDto",
    "TodoResponseDto",
    "UpdateTodoDto",
]
