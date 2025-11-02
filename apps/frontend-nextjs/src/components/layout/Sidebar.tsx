"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

const navigation = [
  { name: 'Profile', href: '/dashboard/profile', icon: '👤', roles: ['guest', 'admin', 'sysadmin'] },
  { name: 'ToDo', href: '/dashboard/todos', icon: '📝', roles: ['guest', 'admin', 'sysadmin'] },
];

const adminNavigation = [
  { name: 'Admin', href: '/dashboard/admin', icon: '🔧', roles: ['admin', 'sysadmin'] },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();

  const allNavigation = [
    ...adminNavigation.filter(item => user && item.roles.includes(user.role)),
    ...navigation.filter(item => user && item.roles.includes(user.role)),
  ];

  return (
    <aside className="w-64 border-r border-border bg-surface-primary min-h-[calc(100vh-4rem)] sticky top-16 hidden md:block">
      <nav className="flex flex-col gap-2 p-4">
        {allNavigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
