"use client";

import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/store';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { refreshToken, loadUser, _hasHydrated } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Wait for Zustand to hydrate from storage
    if (!_hasHydrated) {
      return;
    }

    const initializeAuth = async () => {
      // If we have a refresh token, try to restore the session
      if (refreshToken) {
        try {
          await loadUser();
        } catch (error) {
          console.error('Failed to restore session:', error);
        }
      }
      setIsInitialized(true);
    };

    initializeAuth();
  }, [_hasHydrated, refreshToken, loadUser]); // Re-run when hydration completes

  // Show loading state while initializing
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
