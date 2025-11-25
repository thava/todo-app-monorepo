// Form validation utilities

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength (minimum 8 characters)
 */
export function isValidPassword(password: string): boolean {
  return password.length >= 8;
}

/**
 * Get password strength indicator
 */
export function getPasswordStrength(password: string): {
  strength: 'weak' | 'medium' | 'strong';
  message: string;
} {
  if (password.length < 8) {
    return { strength: 'weak', message: 'Password must be at least 8 characters' };
  }

  let score = 0;

  // Check length
  if (password.length >= 12) score++;
  if (password.length >= 16) score++;

  // Check for lowercase
  if (/[a-z]/.test(password)) score++;

  // Check for uppercase
  if (/[A-Z]/.test(password)) score++;

  // Check for numbers
  if (/\d/.test(password)) score++;

  // Check for special characters
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  if (score < 3) {
    return { strength: 'weak', message: 'Weak password' };
  } else if (score < 5) {
    return { strength: 'medium', message: 'Medium password' };
  } else {
    return { strength: 'strong', message: 'Strong password' };
  }
}

/**
 * Validate full name (non-empty)
 */
export function isValidFullName(fullName: string): boolean {
  return fullName.trim().length > 0;
}
