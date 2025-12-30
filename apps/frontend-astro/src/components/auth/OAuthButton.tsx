import React from 'react';

interface OAuthButtonProps {
  provider: 'google' | 'microsoft';
  mode: 'login' | 'link';
  disabled?: boolean;
  accessToken?: string; // Required for link mode
}

const GoogleIcon = () => (
  <svg className="h-5 w-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const MicrosoftIcon = () => (
  <svg className="h-5 w-5" viewBox="0 0 23 23">
    <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
    <path fill="#f35325" d="M1 1h10v10H1z"/>
    <path fill="#81bc06" d="M12 1h10v10H12z"/>
    <path fill="#05a6f0" d="M1 12h10v10H1z"/>
    <path fill="#ffba08" d="M12 12h10v10H12z"/>
  </svg>
);

export function OAuthButton({ provider, mode, disabled = false, accessToken }: OAuthButtonProps) {
  const handleClick = () => {
    if (disabled) return;

    const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:3001';
    const redirectUrl = `${window.location.origin}/auth-complete`;

    if (mode === 'login') {
      // For login, navigate to OAuth login endpoint
      const authUrl = `${apiUrl}/oauth/${provider}/login?redirect=${encodeURIComponent(redirectUrl)}&frontend=astro`;
      window.location.href = authUrl;
    } else {
      // For link, create and submit POST form with access_token
      if (!accessToken) {
        console.error('Access token is required for link mode');
        return;
      }

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
    }
  };

  const Icon = provider === 'google' ? GoogleIcon : MicrosoftIcon;
  const label = mode === 'login'
    ? `Continue with ${provider === 'google' ? 'Google' : 'Microsoft'}`
    : `Link ${provider === 'google' ? 'Google' : 'Microsoft'} Account`;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className="w-full flex items-center justify-center gap-3 px-4 py-2 border border-border rounded-lg bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-foreground font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Icon />
      {label}
    </button>
  );
}
