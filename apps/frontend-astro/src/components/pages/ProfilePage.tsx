import React, { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { IdentityCard } from '@/components/profile/IdentityCard';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { api } from '@/lib/api';

export function ProfilePage() {
  const { user, accessToken, loadUser } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [unlinkConfirm, setUnlinkConfirm] = useState<{
    isOpen: boolean;
    provider: 'google' | 'microsoft' | null;
  }>({ isOpen: false, provider: null });

  if (!user) {
    return null;
  }

  // Identity detection
  const hasLocalIdentity = !!user.localUsername;
  const hasGoogleIdentity = !!user.googleEmail;
  const hasMicrosoftIdentity = !!user.msEmail;
  const identityCount = [hasLocalIdentity, hasGoogleIdentity, hasMicrosoftIdentity].filter(Boolean).length;

  const canUnlinkGoogle = hasGoogleIdentity && identityCount > 1;
  const canUnlinkMicrosoft = hasMicrosoftIdentity && identityCount > 1;

  const handleLinkProvider = (provider: 'google' | 'microsoft') => {
    if (!accessToken) return;

    const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:3001';
    const redirectUrl = `${window.location.origin}/auth-complete`;

    // Create and submit POST form with redirect, frontend, access_token
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
    frontendInput.value = 'astro';
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

  const handleUnlinkProvider = (provider: 'google' | 'microsoft') => {
    setUnlinkConfirm({ isOpen: true, provider });
  };

  const confirmUnlink = async () => {
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

      // Reload user profile
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

  return (
    <div>
      <h1 className="text-3xl font-bold text-foreground mb-8">Profile</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
        </div>
      )}

      <div className="space-y-6 max-w-2xl">
        {/* Basic Profile Info */}
        <div className="bg-surface-primary rounded-xl shadow-md border border-border p-6 sm:p-8">
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

        {/* Linked Identities Section */}
        <div className="bg-surface-primary rounded-xl shadow-md border border-border p-6 sm:p-8">
          <h2 className="text-xl font-semibold text-foreground mb-2">Linked Identities</h2>
          <p className="text-sm text-muted mb-6">
            Manage your authentication methods. You must have at least one identity linked.
          </p>

          <div className="space-y-3">
            <IdentityCard
              provider="local"
              isLinked={hasLocalIdentity}
              identifier={user.localUsername}
              canUnlink={false}
              isProcessing={isProcessing}
            />

            <IdentityCard
              provider="google"
              isLinked={hasGoogleIdentity}
              identifier={user.googleEmail}
              canUnlink={canUnlinkGoogle}
              onLink={() => handleLinkProvider('google')}
              onUnlink={() => handleUnlinkProvider('google')}
              isProcessing={isProcessing}
            />

            <IdentityCard
              provider="microsoft"
              isLinked={hasMicrosoftIdentity}
              identifier={user.msEmail}
              canUnlink={canUnlinkMicrosoft}
              onLink={() => handleLinkProvider('microsoft')}
              onUnlink={() => handleUnlinkProvider('microsoft')}
              isProcessing={isProcessing}
            />
          </div>

          {identityCount === 1 && (
            <p className="mt-4 text-sm text-yellow-600 dark:text-yellow-400">
              You cannot unlink your last identity. Please link another account first.
            </p>
          )}
        </div>
      </div>

      {/* Unlink Confirmation Dialog */}
      <ConfirmDialog
        isOpen={unlinkConfirm.isOpen}
        title="Unlink Account"
        message={`Are you sure you want to unlink your ${unlinkConfirm.provider} account? You will no longer be able to sign in using ${unlinkConfirm.provider}.`}
        confirmLabel="Unlink"
        onConfirm={confirmUnlink}
        onCancel={() => setUnlinkConfirm({ isOpen: false, provider: null })}
      />
    </div>
  );
}
