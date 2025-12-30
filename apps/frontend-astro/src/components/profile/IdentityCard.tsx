import React from 'react';

interface IdentityCardProps {
  provider: 'local' | 'google' | 'microsoft';
  isLinked: boolean;
  identifier?: string | null; // Username for local, email for OAuth
  canUnlink: boolean;
  onLink?: () => void;
  onUnlink?: () => void;
  isProcessing?: boolean;
}

const LocalIcon = () => (
  <svg className="h-6 w-6 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const GoogleIcon = () => (
  <svg className="h-6 w-6" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const MicrosoftIcon = () => (
  <svg className="h-6 w-6" viewBox="0 0 23 23">
    <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
    <path fill="#f35325" d="M1 1h10v10H1z"/>
    <path fill="#81bc06" d="M12 1h10v10H12z"/>
    <path fill="#05a6f0" d="M1 12h10v10H1z"/>
    <path fill="#ffba08" d="M12 12h10v10H12z"/>
  </svg>
);

export function IdentityCard({
  provider,
  isLinked,
  identifier,
  canUnlink,
  onLink,
  onUnlink,
  isProcessing = false,
}: IdentityCardProps) {
  const getIcon = () => {
    switch (provider) {
      case 'local':
        return <LocalIcon />;
      case 'google':
        return <GoogleIcon />;
      case 'microsoft':
        return <MicrosoftIcon />;
    }
  };

  const getTitle = () => {
    switch (provider) {
      case 'local':
        return 'Local Account';
      case 'google':
        return 'Google Account';
      case 'microsoft':
        return 'Microsoft Account';
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border border-border rounded-lg bg-surface-primary">
      <div className="flex items-center gap-4">
        {getIcon()}
        <div>
          <h3 className="font-medium text-foreground">{getTitle()}</h3>
          {isLinked ? (
            <p className="text-sm text-muted">{identifier}</p>
          ) : (
            <p className="text-sm text-muted">Not linked</p>
          )}
        </div>
      </div>

      <div>
        {isLinked ? (
          canUnlink && onUnlink && (
            <button
              type="button"
              onClick={onUnlink}
              disabled={isProcessing}
              className="px-3 py-1.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Unlink
            </button>
          )
        ) : (
          onLink && (
            <button
              type="button"
              onClick={onLink}
              disabled={isProcessing}
              className="px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Link
            </button>
          )
        )}
      </div>
    </div>
  );
}
