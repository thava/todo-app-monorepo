<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-surface-secondary">
      <div class="max-w-md w-full">
        <div class="bg-surface-primary rounded-lg shadow-lg p-8">
          <!-- Success State -->
          <div v-if="resetSuccess" class="text-center">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-success-100 dark:bg-success-900 mb-4">
              <svg class="h-8 w-8 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Password Reset Successful!</h2>
            <p class="text-muted mb-6">
              Your password has been successfully reset. You can now log in with your new password.
            </p>
            <NuxtLink to="/login">
              <Button class="w-full">
                Go to Login
              </Button>
            </NuxtLink>
          </div>

          <!-- Reset Form -->
          <div v-else-if="!invalidToken">
            <div class="text-center mb-8">
              <h2 class="text-3xl font-bold text-foreground">Set New Password</h2>
              <p class="mt-2 text-sm text-muted">
                Enter your new password below.
              </p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div>
                <Input
                  id="password"
                  v-model="form.password"
                  type="password"
                  label="New Password"
                  placeholder="••••••••"
                  required
                  :error="errors.password"
                  :hint="passwordHint"
                />
                <div v-if="form.password" class="mt-2">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        :class="passwordStrengthClass"
                        class="h-full transition-all duration-300"
                        :style="{ width: passwordStrengthWidth }"
                      ></div>
                    </div>
                    <span class="text-xs text-muted">{{ passwordStrength.message }}</span>
                  </div>
                </div>
              </div>

              <Input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                label="Confirm New Password"
                placeholder="••••••••"
                required
                :error="errors.confirmPassword"
              />

              <Button
                type="submit"
                class="w-full"
                :loading="loading"
                :disabled="loading"
              >
                Reset Password
              </Button>
            </form>
          </div>

          <!-- Invalid Token State -->
          <div v-else class="text-center">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-error-100 dark:bg-error-900 mb-4">
              <svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Invalid or Expired Link</h2>
            <p class="text-muted mb-6">
              The password reset link is invalid or has expired. Please request a new one.
            </p>
            <div class="space-y-3">
              <NuxtLink to="/forgot-password">
                <Button class="w-full">
                  Request New Link
                </Button>
              </NuxtLink>
              <NuxtLink to="/login">
                <Button variant="secondary" class="w-full">
                  Back to Login
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
const toast = useToast();

const form = reactive({
  password: '',
  confirmPassword: '',
});

const errors = reactive({
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const resetSuccess = ref(false);
const invalidToken = ref(false);

const token = computed(() => route.query.token as string);

const passwordStrength = computed(() => {
  return getPasswordStrength(form.password);
});

const passwordStrengthWidth = computed(() => {
  if (passwordStrength.value.strength === 'weak') return '33%';
  if (passwordStrength.value.strength === 'medium') return '66%';
  return '100%';
});

const passwordStrengthClass = computed(() => {
  if (passwordStrength.value.strength === 'weak') return 'bg-error-500';
  if (passwordStrength.value.strength === 'medium') return 'bg-warning-500';
  return 'bg-success-500';
});

const passwordHint = computed(() => {
  if (!form.password) return 'Minimum 8 characters';
  return '';
});

// Check if token is provided on mount
onMounted(() => {
  if (!token.value) {
    invalidToken.value = true;
  }
});

const validateForm = () => {
  errors.password = '';
  errors.confirmPassword = '';

  let isValid = true;

  if (!form.password) {
    errors.password = 'Password is required';
    isValid = false;
  } else if (!isValidPassword(form.password)) {
    errors.password = 'Password must be at least 8 characters';
    isValid = false;
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password';
    isValid = false;
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match';
    isValid = false;
  }

  return isValid;
};

const handleSubmit = async () => {
  if (!validateForm()) return;

  if (!token.value) {
    invalidToken.value = true;
    return;
  }

  loading.value = true;

  try {
    await api.resetPassword({
      token: token.value,
      newPassword: form.password,
    });

    resetSuccess.value = true;
    toast.success('Password reset successful!');
  } catch (error: any) {
    console.error('Password reset error:', error);

    if (error.message?.includes('expired') || error.message?.includes('invalid')) {
      invalidToken.value = true;
      toast.error('The reset link is invalid or has expired.');
    } else {
      toast.error(error.message || 'Failed to reset password. Please try again.');
    }
  } finally {
    loading.value = false;
  }
};

definePageMeta({
  middleware: undefined, // Public page
});
</script>
