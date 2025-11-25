// Token utility functions

/**
 * Decode a JWT token to extract payload
 */
export function decodeJWT(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
}

/**
 * Check if a JWT token is expired
 */
export function isTokenExpired(token: string): boolean {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) return true;

  // Check if token expires in the next 30 seconds
  const expirationTime = decoded.exp * 1000;
  const now = Date.now();
  return expirationTime < now + 30000; // 30 second buffer
}

/**
 * Get the expiration time of a JWT token
 */
export function getTokenExpiration(token: string): number | null {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) return null;

  return decoded.exp * 1000; // Convert to milliseconds
}

/**
 * Check if token needs refresh (expires in less than 5 minutes)
 */
export function shouldRefreshToken(token: string): boolean {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) return true;

  const expirationTime = decoded.exp * 1000;
  const now = Date.now();
  const fiveMinutes = 5 * 60 * 1000;

  return expirationTime < now + fiveMinutes;
}
