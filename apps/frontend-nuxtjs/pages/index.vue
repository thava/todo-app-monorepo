<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1">
      <!-- Hero Section -->
      <section class="bg-gradient-to-b from-primary-50 to-white dark:from-gray-900 dark:to-gray-800 py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Manage Your Tasks with <span class="text-primary-600 dark:text-primary-400">TodoApp</span>
          </h1>
          <p class="text-xl text-muted mb-8 max-w-2xl mx-auto">
            A modern, powerful todo application with authentication, role-based access control, and a beautiful interface.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <template v-if="!isAuthenticated">
              <NuxtLink to="/register" class="w-full sm:w-auto">
                <Button size="lg">
                  Get Started
                </Button>
              </NuxtLink>
              <NuxtLink to="/login" class="w-full sm:w-auto">
                <Button size="lg" variant="secondary">
                  Login
                </Button>
              </NuxtLink>
            </template>
            <NuxtLink v-else to="/dashboard/todos" class="w-full sm:w-auto">
              <Button size="lg">
                Go to Dashboard
              </Button>
            </NuxtLink>
            <NuxtLink to="/about" class="w-full sm:w-auto">
              <Button size="lg" variant="secondary">
                Learn More
              </Button>
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-20 bg-surface-primary">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-center text-foreground mb-12">
            Features
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Feature 1 -->
            <div class="text-center p-6 bg-surface-secondary rounded-lg">
              <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4 flex-shrink-0">
                <svg class="w-6 h-6 text-primary-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-foreground mb-2">Task Management</h3>
              <p class="text-muted">Create, edit, and organize your todos with priorities and due dates.</p>
            </div>

            <!-- Feature 2 -->
            <div class="text-center p-6 bg-surface-secondary rounded-lg">
              <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4 flex-shrink-0">
                <svg class="w-6 h-6 text-primary-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-foreground mb-2">Secure Authentication</h3>
              <p class="text-muted">Email verification, password reset, and JWT-based authentication.</p>
            </div>

            <!-- Feature 3 -->
            <div class="text-center p-6 bg-surface-secondary rounded-lg">
              <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4 flex-shrink-0">
                <svg class="w-6 h-6 text-primary-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-foreground mb-2">Dark Mode</h3>
              <p class="text-muted">Beautiful interface with light and dark themes.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="py-20 bg-primary-600 dark:bg-primary-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 class="text-3xl font-bold text-white mb-4">
            Ready to Get Organized?
          </h2>
          <p class="text-xl text-primary-100 mb-8">
            Start managing your tasks efficiently today.
          </p>
          <NuxtLink v-if="!isAuthenticated" to="/register">
            <Button size="lg" variant="secondary">
              Sign Up Now
            </Button>
          </NuxtLink>
          <NuxtLink v-else to="/dashboard/todos">
            <Button size="lg" variant="secondary">
              Go to Dashboard
            </Button>
          </NuxtLink>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
const { isAuthenticated } = useAuth();

definePageMeta({
  middleware: undefined, // Public page
});
</script>
