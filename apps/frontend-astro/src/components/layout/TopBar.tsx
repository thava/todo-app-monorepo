import React from 'react';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { useAuthStore } from '@/lib/store';

export function TopBar() {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full border-b border-border bg-surface-primary shadow-sm">
      <div className="container mx-auto px-4 flex justify-between items-center h-16 max-w-7xl">
        {/* Left Side - Logo, About, and Dashboard */}
        <div className="flex items-center space-x-8">
          <a href="/" className="flex items-center gap-2 text-xl font-bold hover:text-primary-600 transition-colors no-underline">
            <span className="text-2xl">✓</span>
            <span>TodoGizmo</span>
          </a>

          <a
            href="/about"
            className="px-4 py-2 rounded-lg text-md font-medium text-foreground hover:bg-surface-secondary transition-colors no-underline"
          >
            About
          </a>

          {isAuthenticated && (
            <a
              href="/dashboard"
              className="px-4 py-2 rounded-lg text-md font-medium text-foreground hover:bg-surface-secondary transition-colors no-underline"
            >
              Dashboard
            </a>
          )}
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
              <a
                href="/login"
                className="px-4 py-2 text-md font-medium text-foreground hover:bg-surface-secondary hover:text-primary-600 rounded-lg transition-colors no-underline"
              >
                Login
              </a>
              <a
                href="/register"
                className="px-4 py-2 text-md font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors shadow-sm no-underline"
              >
                Register
              </a>
            </>
          )}

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
