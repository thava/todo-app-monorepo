<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-surface-secondary">
      <div class="max-w-md w-full">
        <div class="bg-surface-primary rounded-lg shadow-lg p-8 text-center">
          <!-- Loading State -->
          <div v-if="verifying">
            <LoadingSpinner size="lg" center />
            <p class="mt-4 text-muted">Verifying your email...</p>
          </div>

          <!-- Success State -->
          <div v-else-if="success">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-success-100 dark:bg-success-900 mb-4">
              <svg class="h-8 w-8 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Email Verified!</h2>
            <p class="text-muted mb-6">
              Your email has been successfully verified. You can now log in to your account.
            </p>
            <NuxtLink to="/login">
              <Button class="w-full">
                Go to Login
              </Button>
            </NuxtLink>
          </div>

          <!-- Error State -->
          <div v-else>
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-error-100 dark:bg-error-900 mb-4">
              <svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Verification Failed</h2>
            <p class="text-muted mb-6">
              {{ errorMessage }}
            </p>
            <div class="space-y-3">
              <NuxtLink to="/login">
                <Button variant="secondary" class="w-full">
                  Go to Login
                </Button>
              </NuxtLink>
              <NuxtLink to="/register">
                <Button variant="ghost" class="w-full">
                  Create New Account
                </Button>
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const api = useApi();

const verifying = ref(true);
const success = ref(false);
const errorMessage = ref('The verification link is invalid or has expired.');

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    verifying.value = false;
    errorMessage.value = 'No verification token provided.';
    return;
  }

  try {
    await api.verifyEmail(token);
    success.value = true;
  } catch (error: any) {
    console.error('Email verification error:', error);
    success.value = false;

    if (error.message?.includes('expired')) {
      errorMessage.value = 'The verification link has expired. Please request a new one.';
    } else if (error.message?.includes('invalid')) {
      errorMessage.value = 'The verification link is invalid. Please check your email or request a new link.';
    } else {
      errorMessage.value = error.message || 'Email verification failed. Please try again.';
    }
  } finally {
    verifying.value = false;
  }
});

definePageMeta({
  middleware: undefined, // Public page
});
</script>
