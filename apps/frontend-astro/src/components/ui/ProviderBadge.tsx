import React from 'react';

interface ProviderBadgeProps {
  provider: 'local' | 'google' | 'microsoft';
  email: string;
}

export function ProviderBadge({ provider, email }: ProviderBadgeProps) {
  const getBadgeStyles = () => {
    switch (provider) {
      case 'local':
        return 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300';
      case 'google':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300';
      case 'microsoft':
        return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300';
    }
  };

  const getLabel = () => {
    switch (provider) {
      case 'local':
        return 'Local';
      case 'google':
        return 'Google';
      case 'microsoft':
        return 'Microsoft';
    }
  };

  return (
    <div className="flex items-center gap-2">
      <span className={`text-xs px-1.5 py-0.5 rounded ${getBadgeStyles()}`}>
        {getLabel()}
      </span>
      <span className="text-sm text-muted">{email}</span>
    </div>
  );
}
