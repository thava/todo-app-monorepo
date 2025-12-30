"use client";

import React, { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

export default function ProfilePage() {
  const { user, accessToken, loadUser } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [unlinkConfirm, setUnlinkConfirm] = useState<{ isOpen: boolean; provider: 'google' | 'microsoft' | null }>({
    isOpen: false,
    provider: null,
  });

  if (!user) {
    return null;
  }

  // Count linked identities
  const hasLocalIdentity = !!user.localUsername;
  const hasGoogleIdentity = !!user.googleEmail;
  const hasMicrosoftIdentity = !!user.msEmail;

  const identityCount = [hasLocalIdentity, hasGoogleIdentity, hasMicrosoftIdentity].filter(Boolean).length;

  // Can only unlink if there are multiple identities
  const canUnlinkGoogle = hasGoogleIdentity && identityCount > 1;
  const canUnlinkMicrosoft = hasMicrosoftIdentity && identityCount > 1;

  const handleLinkProvider = (provider: 'google' | 'microsoft') => {
    if (!accessToken) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
    const redirectUrl = `${window.location.origin}/auth-complete`;

    // Create a form and submit it to initiate OAuth flow securely
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `${apiUrl}/oauth/${provider}/link`;

    // Add redirect field
    const redirectInput = document.createElement('input');
    redirectInput.type = 'hidden';
    redirectInput.name = 'redirect';
    redirectInput.value = redirectUrl;
    form.appendChild(redirectInput);

    // Add frontend field
    const frontendInput = document.createElement('input');
    frontendInput.type = 'hidden';
    frontendInput.name = 'frontend';
    frontendInput.value = 'nextjs';
    form.appendChild(frontendInput);

    // Add access_token field
    const tokenInput = document.createElement('input');
    tokenInput.type = 'hidden';
    tokenInput.name = 'access_token';
    tokenInput.value = accessToken;
    form.appendChild(tokenInput);

    // Submit form
    document.body.appendChild(form);
    form.submit();
  };

  const handleUnlinkClick = (provider: 'google' | 'microsoft') => {
    setUnlinkConfirm({ isOpen: true, provider });
  };

  const handleUnlinkConfirm = async () => {
    if (!accessToken || !unlinkConfirm.provider) return;

    const provider = unlinkConfirm.provider;
    setUnlinkConfirm({ isOpen: false, provider: null });

    setIsProcessing(true);
    setError('');
    setSuccess('');

    try {
      if (provider === 'google') {
        await api.unlinkGoogle(accessToken);
        setSuccess('Google account unlinked successfully');
      } else {
        await api.unlinkMicrosoft(accessToken);
        setSuccess('Microsoft account unlinked successfully');
      }

      // Reload user to get updated profile
      await loadUser();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to unlink account';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUnlinkCancel = () => {
    setUnlinkConfirm({ isOpen: false, provider: null });
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-foreground mb-8">Profile</h1>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
        </div>
      )}

      {/* Basic Information */}
      <div className="bg-surface-primary rounded-xl shadow-md border border-border p-6 sm:p-8 mb-6">
        <h2 className="text-xl font-semibold text-foreground mb-6">Basic Information</h2>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              Full Name
            </label>
            <p className="text-lg text-foreground">{user.fullName}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted mb-2">
              User ID
            </label>
            <p className="text-sm font-mono text-foreground">{user.id}</p>
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

      {/* Linked Identities */}
      <div className="bg-surface-primary rounded-xl shadow-md border border-border p-6 sm:p-8">
        <h2 className="text-xl font-semibold text-foreground mb-6">Linked Identities</h2>
        <div className="space-y-4">
          {/* Local Identity */}
          <div className="flex items-center justify-between p-4 border border-border rounded-lg">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-800">
                <svg className="h-5 w-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-foreground">Local Account</h3>
                {hasLocalIdentity ? (
                  <p className="text-sm text-muted">{user.localUsername}</p>
                ) : (
                  <p className="text-sm text-muted">Not linked</p>
                )}
              </div>
            </div>
            <div>
              {hasLocalIdentity && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                  Linked
                </span>
              )}
            </div>
          </div>

          {/* Google Identity */}
          <div className="flex items-center justify-between p-4 border border-border rounded-lg">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center h-10 w-10 rounded-full bg-white dark:bg-gray-800 border border-border">
                <svg className="h-6 w-6" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-foreground">Google Account</h3>
                {hasGoogleIdentity ? (
                  <p className="text-sm text-muted">{user.googleEmail}</p>
                ) : (
                  <p className="text-sm text-muted">Not linked</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {hasGoogleIdentity ? (
                <>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                    Linked
                  </span>
                  {canUnlinkGoogle && (
                    <button
                      onClick={() => handleUnlinkClick('google')}
                      disabled={isProcessing}
                      className="px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 border border-red-300 dark:border-red-700 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Unlink
                    </button>
                  )}
                </>
              ) : (
                <button
                  onClick={() => handleLinkProvider('google')}
                  disabled={isProcessing}
                  className="px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 border border-primary-300 dark:border-primary-700 rounded-md hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Link Google
                </button>
              )}
            </div>
          </div>

          {/* Microsoft Identity */}
          <div className="flex items-center justify-between p-4 border border-border rounded-lg">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center h-10 w-10 rounded-full bg-white dark:bg-gray-800 border border-border">
                <svg className="h-6 w-6" viewBox="0 0 23 23">
                  <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
                  <path fill="#f35325" d="M1 1h10v10H1z"/>
                  <path fill="#81bc06" d="M12 1h10v10H12z"/>
                  <path fill="#05a6f0" d="M1 12h10v10H1z"/>
                  <path fill="#ffba08" d="M12 12h10v10H12z"/>
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-foreground">Microsoft Account</h3>
                {hasMicrosoftIdentity ? (
                  <p className="text-sm text-muted">{user.msEmail}</p>
                ) : (
                  <p className="text-sm text-muted">Not linked</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {hasMicrosoftIdentity ? (
                <>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                    Linked
                  </span>
                  {canUnlinkMicrosoft && (
                    <button
                      onClick={() => handleUnlinkClick('microsoft')}
                      disabled={isProcessing}
                      className="px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 border border-red-300 dark:border-red-700 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Unlink
                    </button>
                  )}
                </>
              ) : (
                <button
                  onClick={() => handleLinkProvider('microsoft')}
                  disabled={isProcessing}
                  className="px-4 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 border border-primary-300 dark:border-primary-700 rounded-md hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Link Microsoft
                </button>
              )}
            </div>
          </div>
        </div>

        {identityCount === 1 && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-600 dark:text-blue-400">
              <strong>Note:</strong> You must have at least one linked identity. Link another account before unlinking your current one.
            </p>
          </div>
        )}
      </div>

      {/* Unlink Confirmation Dialog */}
      <ConfirmDialog
        isOpen={unlinkConfirm.isOpen}
        title="Unlink Account"
        message={
          unlinkConfirm.provider
            ? `Are you sure you want to unlink your ${unlinkConfirm.provider === 'google' ? 'Google' : 'Microsoft'} account? You can link it again later if needed.`
            : ''
        }
        confirmLabel="Unlink"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={handleUnlinkConfirm}
        onCancel={handleUnlinkCancel}
      />
    </div>
  );
}
