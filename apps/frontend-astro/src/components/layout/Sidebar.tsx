import React from 'react';

interface SidebarProps {
  currentPath: string;
}

export function Sidebar({ currentPath }: SidebarProps) {
  const isActive = (path: string) => currentPath === path;

  return (
    <aside className="w-64 bg-surface-primary border-r border-border min-h-[calc(100vh-4rem)]">
      <nav className="p-4 space-y-2">
        <a
          href="/dashboard/profile"
          className={`sidebar-link ${isActive('/dashboard/profile') ? 'active' : ''}`}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span>Profile</span>
        </a>
        <a
          href="/dashboard/todos"
          className={`sidebar-link ${isActive('/dashboard/todos') ? 'active' : ''}`}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <span>Todos</span>
        </a>

      </nav>
    </aside>
  );
}
