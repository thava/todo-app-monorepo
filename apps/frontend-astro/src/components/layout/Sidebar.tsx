import React from 'react';
import { useAuthStore } from '@/lib/store';

interface SidebarProps {
  currentPath: string;
}

const navigation = [
  { name: 'Profile', href: '/dashboard/profile', icon: '👤', roles: ['guest', 'admin', 'sysadmin'] },
  { name: 'Todos', href: '/dashboard/todos', icon: '📝', roles: ['guest', 'admin', 'sysadmin'] },
];

const adminNavigation = [
  { name: 'Users', href: '/dashboard/admin', icon: '🔧', roles: ['admin', 'sysadmin'] },
];

export function Sidebar({ currentPath }: SidebarProps) {
  const { user } = useAuthStore();
  const isActive = (path: string) => currentPath === path;

  const allNavigation = [
    ...adminNavigation.filter(item => user && item.roles.includes(user.role)),
    ...navigation.filter(item => user && item.roles.includes(user.role)),
  ];

  return (
    <aside className="w-64 bg-surface-primary border-r border-border min-h-[calc(100vh-4rem)]">
      <nav className="p-4 space-y-2">
        {allNavigation.map((item) => (
          <a
            key={item.name}
            href={item.href}
            className={`sidebar-link ${isActive(item.href) ? 'active' : ''}`}
          >
            <span className="text-xl">{item.icon}</span>
            <span>{item.name}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}
