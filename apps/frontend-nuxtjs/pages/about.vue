<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 py-12">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-4xl font-bold text-foreground mb-6">About TodoApp</h1>

        <div class="prose dark:prose-invert max-w-none">
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-foreground mb-4">What is TodoApp?</h2>
            <p class="text-muted mb-4">
              TodoApp is a modern, full-featured task management application built with cutting-edge web technologies.
              It provides a seamless experience for managing your daily tasks with features like priorities, due dates,
              and a beautiful interface that adapts to your preferences.
            </p>
          </section>

          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-foreground mb-4">Key Features</h2>
            <ul class="list-disc list-inside text-muted space-y-2">
              <li>✓ Secure authentication with email verification</li>
              <li>✓ Password reset functionality</li>
              <li>✓ Create, edit, and delete todos</li>
              <li>✓ Set priorities (low, medium, high) and due dates</li>
              <li>✓ Role-based access control (guest, admin, sysadmin)</li>
              <li>✓ Dark mode support</li>
              <li>✓ Responsive design for all devices</li>
              <li>✓ Admin panel for user management</li>
            </ul>
          </section>

          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-foreground mb-4">Technology Stack</h2>
            <div class="bg-surface-secondary p-6 rounded-lg">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-muted">
                <div>
                  <h3 class="font-semibold text-foreground mb-2">Frontend</h3>
                  <ul class="space-y-1">
                    <li>• Nuxt 3</li>
                    <li>• Vue 3</li>
                    <li>• TypeScript</li>
                    <li>• Tailwind CSS</li>
                    <li>• Pinia (State Management)</li>
                  </ul>
                </div>
                <div>
                  <h3 class="font-semibold text-foreground mb-2">Backend</h3>
                  <ul class="space-y-1">
                    <li>• NestJS</li>
                    <li>• PostgreSQL</li>
                    <li>• JWT Authentication</li>
                    <li>• TypeORM</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-foreground mb-4">User Roles</h2>
            <div class="space-y-4">
              <div class="bg-surface-secondary p-4 rounded-lg">
                <h3 class="font-semibold text-foreground mb-2">Guest</h3>
                <p class="text-muted">Basic user role with access to personal todos and profile management.</p>
              </div>
              <div class="bg-surface-secondary p-4 rounded-lg">
                <h3 class="font-semibold text-foreground mb-2">Admin</h3>
                <p class="text-muted">Can view all users and todos in the system. Has access to the admin panel.</p>
              </div>
              <div class="bg-surface-secondary p-4 rounded-lg">
                <h3 class="font-semibold text-foreground mb-2">Sysadmin</h3>
                <p class="text-muted">Full system access including user management (create, edit, delete users).</p>
              </div>
            </div>
          </section>

          <section>
            <h2 class="text-2xl font-semibold text-foreground mb-4">Get Started</h2>
            <p class="text-muted mb-4">
              Ready to organize your tasks? Sign up now and start managing your todos efficiently.
            </p>
            <div class="flex gap-4">
              <NuxtLink v-if="!isAuthenticated" to="/register">
                <Button>Create Account</Button>
              </NuxtLink>
              <NuxtLink v-else to="/dashboard/todos">
                <Button>Go to Dashboard</Button>
              </NuxtLink>
            </div>
          </section>
        </div>
      </div>
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
