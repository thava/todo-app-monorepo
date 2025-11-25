<template>
  <aside class="w-64 bg-surface-primary border-r border-border min-h-screen p-4">
    <nav class="space-y-1">
      <!-- Todos Link -->
      <NuxtLink
        to="/dashboard/todos"
        class="sidebar-link"
        :class="{ active: isActive('/dashboard/todos') }"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        <span>Todos</span>
      </NuxtLink>

      <!-- Profile Link -->
      <NuxtLink
        to="/dashboard/profile"
        class="sidebar-link"
        :class="{ active: isActive('/dashboard/profile') }"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </svg>
        <span>Profile</span>
      </NuxtLink>

      <!-- Admin Link (admin/sysadmin only) -->
      <NuxtLink
        v-if="isAdmin"
        to="/dashboard/admin"
        class="sidebar-link"
        :class="{ active: isActive('/dashboard/admin') }"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        <span>Admin</span>
      </NuxtLink>

      <!-- Divider -->
      <div class="pt-4 mt-4 border-t border-border">
        <!-- User Info -->
        <div class="px-4 py-3 bg-surface-secondary rounded-lg">
          <div class="text-sm font-medium text-foreground">
            {{ user?.fullName }}
          </div>
          <div class="text-xs text-muted">{{ user?.email }}</div>
          <div class="mt-2 flex items-center space-x-2">
            <span
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
              :class="roleClass"
            >
              {{ user?.role }}
            </span>
            <span
              v-if="isEmailVerified"
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-50 text-success-600"
              title="Email verified"
            >
              ✓ Verified
            </span>
            <span
              v-else
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-warning-50 text-warning-600"
              title="Email not verified"
            >
              ! Unverified
            </span>
          </div>
        </div>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
const route = useRoute();
const { user, isAdmin, isEmailVerified } = useAuth();

const isActive = (path: string) => {
  return route.path === path;
};

const roleClass = computed(() => {
  switch (user.value?.role) {
    case 'sysadmin':
      return 'bg-error-50 text-error-600';
    case 'admin':
      return 'bg-warning-50 text-warning-600';
    default:
      return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300';
  }
});
</script>
