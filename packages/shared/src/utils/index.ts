/**
 * Format error response
 */
export function formatError(
  code: string,
  message: string,
  details?: unknown,
  path?: string,
  requestId?: string
) {
  return {
    error: {
      code,
      message,
      details,
      timestamp: new Date().toISOString(),
      path,
      requestId,
    },
  };
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if email is valid format (simple check)
 */
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Sanitize string for display
 */
export function sanitizeString(str: string): string {
  return str.trim().replace(/\s+/g, ' ');
}
