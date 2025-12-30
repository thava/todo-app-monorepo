import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/store';

type Status = 'processing' | 'success' | 'linked' | 'error';

export function AuthCompletePage() {
  const { _hasHydrated, setAuth, loadUser } = useAuthStore();
  const [status, setStatus] = useState<Status>('processing');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    // Critical: Wait for store hydration before processing
    if (!_hasHydrated) return;

    processAuthCallback();
  }, [_hasHydrated, setAuth, loadUser]);

  const getRememberMePreference = (): boolean => {
    // Check if auth data exists in localStorage or sessionStorage
    const hasLocalStorage = localStorage.getItem('auth-storage') !== null;
    const hasSessionStorage = sessionStorage.getItem('auth-storage') !== null;
    return hasLocalStorage || !hasSessionStorage; // Default to true
  };

  const isValidJWT = (token: string): boolean => {
    return token.split('.').length === 3; // Basic JWT structure check
  };

  const sanitizeMessage = (msg: string): string => {
    return msg.replace(/[<>]/g, ''); // Remove HTML tags
  };

  const processAuthCallback = async () => {
    try {
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);

      // Check for error from OAuth callback
      const error = params.get('error');
      const errorMessage = params.get('message');

      if (error) {
        setStatus('error');
        const sanitized = errorMessage ? sanitizeMessage(decodeURIComponent(errorMessage)) : 'OAuth authentication failed';
        setMessage(sanitized);
        return;
      }

      const accessToken = params.get('access_token');
      const refreshToken = params.get('refresh_token');
      const linkStatus = params.get('status');
      const linkProvider = params.get('provider');

      // Handle account linking success
      if (linkStatus === 'linked' && linkProvider) {
        setStatus('linked');
        setMessage(`Successfully linked your ${linkProvider} account!`);

        setTimeout(() => {
          window.location.href = '/dashboard/profile';
        }, 2000);
        return;
      }

      // Handle login success
      if (!accessToken || !refreshToken) {
        setStatus('error');
        setMessage('Authentication failed. Missing tokens.');
        return;
      }

      // Validate token format
      if (!isValidJWT(accessToken) || !isValidJWT(refreshToken)) {
        setStatus('error');
        setMessage('Authentication failed. Invalid token format.');
        return;
      }

      // Clear URL fragment from browser history
      window.history.replaceState({}, document.title, window.location.pathname);

      // Determine rememberMe preference
      const rememberMe = getRememberMePreference();

      // Store tokens temporarily, then load full user profile
      setAuth({ id: '', email: '', fullName: '', role: 'guest', emailVerified: true }, accessToken, refreshToken, rememberMe);

      await loadUser();

      setStatus('success');
      setMessage('Authentication successful! Redirecting...');

      setTimeout(() => {
        window.location.href = '/dashboard/todos';
      }, 1500);
    } catch (error) {
      console.error('Auth callback error:', error);
      setStatus('error');
      setMessage('Authentication failed. Please try again.');
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return (
          <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'success':
      case 'linked':
        return (
          <svg className="h-12 w-12 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="h-12 w-12 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-primary-600';
      case 'success':
      case 'linked':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md">
        <div className="bg-surface-primary rounded-xl shadow-lg p-8 border border-border text-center">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>

          <h1 className={`text-2xl font-bold mb-2 ${getStatusColor()}`}>
            {status === 'processing' && 'Processing...'}
            {status === 'success' && 'Success!'}
            {status === 'linked' && 'Account Linked!'}
            {status === 'error' && 'Authentication Failed'}
          </h1>

          <p className="text-muted mb-6">{message}</p>

          {status === 'error' && (
            <div className="space-y-3">
              <a
                href="/login"
                className="block w-full py-2 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
              >
                Try Again
              </a>
              <a
                href="/"
                className="block w-full py-2 px-4 border border-border hover:bg-surface-secondary text-foreground font-medium rounded-lg transition-colors"
              >
                Go Home
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
