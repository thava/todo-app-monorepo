<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-surface-secondary">
      <div class="max-w-md w-full">
        <div class="bg-surface-primary rounded-lg shadow-lg p-8">
          <!-- Success Message -->
          <div v-if="registrationSuccess" class="text-center">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-success-100 dark:bg-success-900 mb-4">
              <svg class="h-8 w-8 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-foreground mb-4">Check Your Email</h2>
            <p class="text-muted mb-6">
              We've sent a verification link to <strong class="text-foreground">{{ registeredEmail }}</strong>.
              Please check your inbox and click the link to verify your email address.
            </p>
            <div class="space-y-3">
              <p class="text-sm text-muted">
                Didn't receive the email? Check your spam folder or
                <button @click="resendVerification" class="text-primary-600 hover:text-primary-700 font-medium">
                  resend verification email
                </button>
              </p>
              <NuxtLink to="/login">
                <Button variant="secondary" class="w-full">
                  Go to Login
                </Button>
              </NuxtLink>
            </div>
          </div>

          <!-- Registration Form -->
          <div v-else>
            <div class="text-center mb-8">
              <h2 class="text-3xl font-bold text-foreground">Create Account</h2>
              <p class="mt-2 text-sm text-muted">
                Already have an account?
                <NuxtLink to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
                  Sign in
                </NuxtLink>
              </p>
            </div>

            <form @submit.prevent="handleRegister" class="space-y-6">
              <Input
                id="fullName"
                v-model="form.fullName"
                type="text"
                label="Full Name"
                placeholder="John Doe"
                required
                :error="errors.fullName"
              />

              <Input
                id="email"
                v-model="form.email"
                type="email"
                label="Email"
                placeholder="you@example.com"
                required
                :error="errors.email"
              />

              <div>
                <Input
                  id="password"
                  v-model="form.password"
                  type="password"
                  label="Password"
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
                label="Confirm Password"
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
                Create Account
              </Button>
            </form>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
const { register } = useAuth();
const toast = useToast();
const api = useApi();

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const errors = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const registrationSuccess = ref(false);
const registeredEmail = ref('');

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

const validateForm = () => {
  errors.fullName = '';
  errors.email = '';
  errors.password = '';
  errors.confirmPassword = '';

  let isValid = true;

  if (!form.fullName.trim()) {
    errors.fullName = 'Full name is required';
    isValid = false;
  }

  if (!form.email) {
    errors.email = 'Email is required';
    isValid = false;
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Invalid email format';
    isValid = false;
  }

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

const handleRegister = async () => {
  if (!validateForm()) return;

  loading.value = true;

  try {
    await register({
      email: form.email,
      password: form.password,
      fullName: form.fullName,
    });

    registeredEmail.value = form.email;
    registrationSuccess.value = true;

    toast.success('Registration successful! Please check your email.');
  } catch (error: any) {
    console.error('Registration error:', error);

    if (error.message?.includes('already exists') || error.message?.includes('duplicate')) {
      errors.email = 'This email is already registered';
      toast.error('Email already registered. Please login instead.');
    } else {
      toast.error(error.message || 'Registration failed. Please try again.');
    }
  } finally {
    loading.value = false;
  }
};

const resendVerification = async () => {
  try {
    await api.requestPasswordReset({ email: registeredEmail.value });
    toast.success('Verification email sent! Check your inbox.');
  } catch (error: any) {
    toast.error('Failed to resend email. Please try again later.');
  }
};

definePageMeta({
  middleware: 'guest',
});
</script>
