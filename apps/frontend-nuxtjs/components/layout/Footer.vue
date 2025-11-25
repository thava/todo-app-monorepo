<template>
  <footer class="bg-surface-primary border-t border-border mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-lg font-semibold text-foreground mb-3">TodoApp</h3>
          <p class="text-sm text-muted">
            A modern todo application with authentication and role-based access control.
          </p>
        </div>

        <!-- Links -->
        <div>
          <h3 class="text-lg font-semibold text-foreground mb-3">Quick Links</h3>
          <ul class="space-y-2">
            <li>
              <NuxtLink to="/" class="text-sm text-muted hover:text-primary-600 transition-colors">
                Home
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/about" class="text-sm text-muted hover:text-primary-600 transition-colors">
                About
              </NuxtLink>
            </li>
            <li v-if="isAuthenticated">
              <NuxtLink to="/dashboard/todos" class="text-sm text-muted hover:text-primary-600 transition-colors">
                Dashboard
              </NuxtLink>
            </li>
            <li v-else>
              <NuxtLink to="/login" class="text-sm text-muted hover:text-primary-600 transition-colors">
                Login
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Info -->
        <div>
          <h3 class="text-lg font-semibold text-foreground mb-3">Built With</h3>
          <ul class="space-y-2 text-sm text-muted">
            <li>• Nuxt 3 + Vue 3</li>
            <li>• TypeScript</li>
            <li>• Tailwind CSS</li>
            <li>• Pinia</li>
          </ul>
        </div>
      </div>

      <!-- Bottom -->
      <div class="mt-8 pt-8 border-t border-border">
        <p class="text-center text-sm text-muted">
          &copy; {{ currentYear }} TodoApp. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { isAuthenticated } = useAuth();
const currentYear = new Date().getFullYear();
</script>
