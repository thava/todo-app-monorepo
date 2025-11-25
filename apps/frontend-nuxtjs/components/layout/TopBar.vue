<template>
  <nav class="bg-surface-primary border-b border-border sticky top-0 z-50 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left: Logo and Navigation -->
        <div class="flex">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center">
            <span class="text-xl font-bold text-primary-600">TodoApp</span>
          </NuxtLink>

          <!-- Desktop Navigation -->
          <div class="hidden md:ml-10 md:flex md:items-center md:space-x-4">
            <NuxtLink
              to="/"
              class="navbar-link px-3 py-2 rounded-md text-base font-medium"
            >
              Home
            </NuxtLink>
            <NuxtLink
              to="/about"
              class="navbar-link px-3 py-2 rounded-md text-base font-medium"
            >
              About
            </NuxtLink>
            <NuxtLink
              v-if="isAuthenticated"
              to="/dashboard/todos"
              class="navbar-link px-3 py-2 rounded-md text-base font-medium"
            >
              Dashboard
            </NuxtLink>
          </div>
        </div>

        <!-- Right: Theme Toggle and Auth -->
        <div class="flex items-center space-x-2 sm:space-x-4">
          <!-- Theme Toggle -->
          <div class="flex-shrink-0">
            <ThemeToggle />
          </div>

          <!-- Desktop Auth Links -->
          <div class="hidden md:flex items-center space-x-2">
            <!-- Authenticated User Menu -->
            <template v-if="isAuthenticated">
              <span class="text-sm text-muted">
                {{ user?.fullName }}
              </span>
              <button
                @click="handleLogout"
                class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors whitespace-nowrap"
              >
                Logout
              </button>
            </template>

            <!-- Guest Links -->
            <template v-else>
              <NuxtLink
                to="/login"
                class="px-4 py-2 text-base font-medium text-gray-700 dark:text-gray-200 hover:text-primary-600 dark:hover:text-primary-400 transition-colors whitespace-nowrap"
              >
                Login
              </NuxtLink>
              <NuxtLink
                to="/register"
                class="px-4 py-2 text-base font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors whitespace-nowrap"
              >
                Register
              </NuxtLink>
            </template>
          </div>

          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex-shrink-0"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="md:hidden border-t border-border">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <NuxtLink
          to="/"
          class="block navbar-link px-3 py-2 rounded-md text-base font-medium"
          @click="mobileMenuOpen = false"
        >
          Home
        </NuxtLink>
        <NuxtLink
          to="/about"
          class="block navbar-link px-3 py-2 rounded-md text-base font-medium"
          @click="mobileMenuOpen = false"
        >
          About
        </NuxtLink>
        <NuxtLink
          v-if="isAuthenticated"
          to="/dashboard/todos"
          class="block navbar-link px-3 py-2 rounded-md text-base font-medium"
          @click="mobileMenuOpen = false"
        >
          Dashboard
        </NuxtLink>
        <!-- Mobile Auth Links -->
        <template v-if="!isAuthenticated">
          <NuxtLink
            to="/login"
            class="block navbar-link px-3 py-2 rounded-md text-base font-medium"
            @click="mobileMenuOpen = false"
          >
            Login
          </NuxtLink>
          <NuxtLink
            to="/register"
            class="block navbar-link px-3 py-2 rounded-md text-base font-medium"
            @click="mobileMenuOpen = false"
          >
            Register
          </NuxtLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
const { user, isAuthenticated, logout } = useAuth();
const mobileMenuOpen = ref(false);

const handleLogout = async () => {
  await logout();
  navigateTo('/login');
};
</script>
