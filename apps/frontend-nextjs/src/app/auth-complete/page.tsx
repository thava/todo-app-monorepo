"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function AuthCompletePage() {
  const router = useRouter();
  const { setAuth, loadUser } = useAuthStore();
  const [status, setStatus] = useState<'processing' | 'success' | 'error' | 'linked'>('processing');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    const processAuthCallback = async () => {
      try {
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);

        // Check for error from OAuth callback
        const error = params.get('error');
        const errorMessage = params.get('message');

        if (error) {
          setStatus('error');
          setMessage(errorMessage ? decodeURIComponent(errorMessage) : 'OAuth authentication failed');
          return;
        }

        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const linkStatus = params.get('status');
        const linkProvider = params.get('provider');

        if (linkStatus === 'linked' && linkProvider) {
          setStatus('linked');
          setMessage(`Successfully linked your ${linkProvider} account!`);

          setTimeout(() => {
            router.push('/dashboard/profile');
          }, 2000);
          return;
        }

        if (!accessToken || !refreshToken) {
          setStatus('error');
          setMessage('Authentication failed. Missing tokens.');
          return;
        }

        window.history.replaceState({}, document.title, window.location.pathname);

        setAuth({ id: '', email: '', fullName: '', role: 'guest', emailVerified: true }, accessToken, refreshToken, true);

        await loadUser();

        setStatus('success');
        setMessage('Authentication successful! Redirecting...');

        setTimeout(() => {
          router.push('/dashboard/todos');
        }, 1500);
      } catch (error) {
        console.error('Auth callback error:', error);
        setStatus('error');
        setMessage('Authentication failed. Please try again.');
      }
    };

    processAuthCallback();
  }, [setAuth, loadUser, router]);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="bg-surface-primary rounded-xl shadow-lg p-8 border border-border text-center">
          {status === 'processing' && (
            <>
              <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent mb-4"></div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Processing...</h2>
              <p className="text-muted">{message}</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900/30 mb-4">
                <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Success!</h2>
              <p className="text-muted">{message}</p>
            </>
          )}

          {status === 'linked' && (
            <>
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 dark:bg-blue-900/30 mb-4">
                <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Account Linked!</h2>
              <p className="text-muted">{message}</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30 mb-4">
                <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Error</h2>
              <p className="text-muted mb-4">{message}</p>
              <div className="flex gap-2 justify-center">
                <button
                  onClick={() => router.push('/dashboard/profile')}
                  className="px-4 py-2 bg-surface-secondary hover:bg-surface-primary border border-border text-foreground font-medium rounded-lg transition-colors"
                >
                  Back to Profile
                </button>
                <button
                  onClick={() => router.push('/login')}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                >
                  Back to Login
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
