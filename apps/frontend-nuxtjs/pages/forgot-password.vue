<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-surface-secondary">
      <div class="max-w-md w-full">
        <div class="bg-surface-primary rounded-lg shadow-lg p-8">
          <!-- Success Message -->
          <div v-if="emailSent" class="text-center">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-success-100 dark:bg-success-900 mb-4">
              <svg class="h-8 w-8 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Check Your Email</h2>
            <p class="text-muted mb-6">
              If an account exists with <strong class="text-foreground">{{ form.email }}</strong>,
              you will receive a password reset link shortly.
            </p>
            <div class="space-y-3">
              <p class="text-sm text-muted">
                Didn't receive the email? Check your spam folder or wait a few minutes.
              </p>
              <NuxtLink to="/login">
                <Button variant="secondary" class="w-full">
                  Back to Login
                </Button>
              </NuxtLink>
            </div>
          </div>

          <!-- Request Form -->
          <div v-else>
            <div class="text-center mb-8">
              <h2 class="text-3xl font-bold text-foreground">Reset Password</h2>
              <p class="mt-2 text-sm text-muted">
                Enter your email and we'll send you a link to reset your password.
              </p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-6">
              <Input
                id="email"
                v-model="form.email"
                type="email"
                label="Email"
                placeholder="you@example.com"
                required
                :error="errors.email"
              />

              <Button
                type="submit"
                class="w-full"
                :loading="loading"
                :disabled="loading"
              >
                Send Reset Link
              </Button>

              <div class="text-center">
                <NuxtLink to="/login" class="text-sm text-primary-600 hover:text-primary-700">
                  Back to Login
                </NuxtLink>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const toast = useToast();

const form = reactive({
  email: '',
});

const errors = reactive({
  email: '',
});

const loading = ref(false);
const emailSent = ref(false);

const validateForm = () => {
  errors.email = '';

  if (!form.email) {
    errors.email = 'Email is required';
    return false;
  }

  if (!isValidEmail(form.email)) {
    errors.email = 'Invalid email format';
    return false;
  }

  return true;
};

const handleSubmit = async () => {
  if (!validateForm()) return;

  loading.value = true;

  try {
    await api.requestPasswordReset({ email: form.email });
    emailSent.value = true;
  } catch (error: any) {
    console.error('Password reset request error:', error);
    // Always show success to prevent email enumeration
    emailSent.value = true;
  } finally {
    loading.value = false;
  }
};

definePageMeta({
  middleware: undefined, // Public page
});
</script>
