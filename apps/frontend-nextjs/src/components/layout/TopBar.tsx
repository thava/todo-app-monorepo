"use client";

import React from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { ThemeToggle } from '../theme/ThemeToggle';

export function TopBar() {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full border-b border-border bg-surface-primary shadow-sm">
      <div className="container mx-auto px-4 flex justify-between items-center h-16 max-w-7xl">
        {/* Left Side - Logo and About */}
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold hover:text-primary-600 transition-colors no-underline">
            <span className="text-2xl">✓</span>
            <span>TodoGizmo</span>
          </Link>

          <Link
            href="/about"
            className="px-4 py-2 rounded-lg text-sm font-medium text-foreground hover:bg-surface-secondary transition-colors no-underline"
          >
            About
          </Link>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-muted hidden md:inline">
                {user?.fullName}
              </span>
              <button
                onClick={() => logout()}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-colors shadow-sm"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-foreground hover:bg-surface-secondary hover:text-primary-600 rounded-lg transition-colors no-underline"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-colors shadow-sm no-underline"
              >
                Register
              </Link>
            </>
          )}

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
