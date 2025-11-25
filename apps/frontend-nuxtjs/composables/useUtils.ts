/**
 * Composable for utility functions
 * Provides easy access to common utilities throughout the app
 */
export const useUtils = () => {
  return {
    // Date utilities
    formatDate: (dateString: string | null | undefined) => {
      return formatDate(dateString);
    },
    formatDateTime: (dateString: string | null | undefined) => {
      return formatDateTime(dateString);
    },
    formatDateForInput: (dateString: string | null | undefined) => {
      return formatDateForInput(dateString);
    },
    isPastDue: (dateString: string | null | undefined) => {
      return isPastDue(dateString);
    },
    getRelativeTime: (dateString: string | null | undefined) => {
      return getRelativeTime(dateString);
    },

    // Token utilities
    decodeJWT: (token: string) => {
      return decodeJWT(token);
    },
    isTokenExpired: (token: string) => {
      return isTokenExpired(token);
    },
    getTokenExpiration: (token: string) => {
      return getTokenExpiration(token);
    },
    shouldRefreshToken: (token: string) => {
      return shouldRefreshToken(token);
    },

    // Validation utilities
    isValidEmail: (email: string) => {
      return isValidEmail(email);
    },
    isValidPassword: (password: string) => {
      return isValidPassword(password);
    },
    getPasswordStrength: (password: string) => {
      return getPasswordStrength(password);
    },
    isValidFullName: (fullName: string) => {
      return isValidFullName(fullName);
    },
  };
};
