/**
 * API Error Codes
 */
export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
}

/**
 * Password validation rules
 */
export const PASSWORD_RULES = {
  MIN_LENGTH: 8,
  REQUIRE_UPPERCASE: true,
  REQUIRE_LOWERCASE: true,
  REQUIRE_NUMBER: true,
  REQUIRE_SPECIAL: true,
  MIN_CHARACTER_CLASSES: 3,
} as const;

/**
 * Token expiry times
 */
export const TOKEN_EXPIRY = {
  ACCESS_TOKEN: '15m',
  REFRESH_TOKEN: '7d',
  EMAIL_VERIFICATION: '24h',
  PASSWORD_RESET: '1h',
} as const;

/**
 * Rate limiting
 */
export const RATE_LIMITS = {
  LOGIN: { requests: 5, window: '15m' },
  REGISTER: { requests: 3, window: '1h' },
  PASSWORD_RESET: { requests: 3, window: '1h' },
  DEFAULT: { requests: 100, window: '15m' },
} as const;

/**
 * Session limits
 */
export const SESSION_LIMITS = {
  MAX_SESSIONS_PER_USER: 5,
} as const;
