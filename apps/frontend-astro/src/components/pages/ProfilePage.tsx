import React from 'react';
import { useAuthStore } from '@/lib/store';

export function ProfilePage() {
  const { user } = useAuthStore();

  if (!user) {
    return null;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-foreground mb-8">Profile</h1>

      <div className="bg-surface-primary rounded-xl shadow-md border border-border p-6 sm:p-8 max-w-2xl">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              Full Name
            </label>
            <p className="text-lg text-foreground">{user.fullName}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              Email
            </label>
            <p className="text-lg text-foreground">{user.email}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              Role
            </label>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200">
              {user.role}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              Email Verification Status
            </label>
            <div className="flex items-center gap-2">
              {user.emailVerified ? (
                <>
                  <span className="text-green-500">✓</span>
                  <span className="text-foreground">Verified</span>
                </>
              ) : (
                <>
                  <span className="text-yellow-500">⚠</span>
                  <span className="text-foreground">Not verified</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
