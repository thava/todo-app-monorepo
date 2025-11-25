<template>
  <div class="min-h-screen flex flex-col">
    <TopBar />

    <main class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-surface-secondary">
      <div class="max-w-md w-full">
        <div class="bg-surface-primary rounded-lg shadow-lg p-8">
          <div class="text-center mb-8">
            <h2 class="text-3xl font-bold text-foreground">Sign In</h2>
            <p class="mt-2 text-sm text-muted">
              Don't have an account?
              <NuxtLink to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
                Sign up
              </NuxtLink>
            </p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-6">
            <Input
              id="email"
              v-model="form.email"
              type="email"
              label="Email"
              placeholder="you@example.com"
              required
              :error="errors.email"
            />

            <Input
              id="password"
              v-model="form.password"
              type="password"
              label="Password"
              placeholder="••••••••"
              required
              :error="errors.password"
            />

            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center">
                <input
                  id="remember-me"
                  v-model="form.rememberMe"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="remember-me" class="ml-2 block text-muted">
                  Remember me
                </label>
              </div>

              <NuxtLink to="/forgot-password" class="text-primary-600 hover:text-primary-700">
                Forgot password?
              </NuxtLink>
            </div>

            <Button
              type="submit"
              class="w-full"
              :loading="loading"
              :disabled="loading"
            >
              Sign In
            </Button>
          </form>

          <!-- Demo Users Info -->
          <div v-if="demoUsers.length > 0" class="mt-6 pt-6 border-t border-border">
            <p class="text-sm text-muted text-center mb-3">Demo accounts (for testing):</p>
            <div class="space-y-2">
              <button
                v-for="user in demoUsers"
                :key="user.email"
                @click="fillDemoCredentials(user.email)"
                class="w-full text-left px-3 py-2 text-sm bg-surface-secondary hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                <span class="font-medium text-foreground">{{ user.email }}</span>
                <span class="text-muted ml-2">({{ user.role }})</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
const { login } = useAuth();
const toast = useToast();
const router = useRouter();
const route = useRoute();
const config = useRuntimeConfig();

const form = reactive({
  email: '',
  password: '',
  rememberMe: true,
});

const errors = reactive({
  email: '',
  password: '',
});

const loading = ref(false);

// Parse demo users from config
const demoUsers = computed(() => {
  const domain = config.public.demoDomain;
  const users = config.public.demoUsers;

  if (!domain || !users) return [];

  return users.split(',').map((user: string) => {
    const role = user.includes('admin') ? (user.includes('sys') ? 'sysadmin' : 'admin') : 'guest';
    return {
      email: `${user}@${domain}`,
      role,
    };
  });
});

const fillDemoCredentials = (email: string) => {
  form.email = email;
  form.password = config.public.demoPassword || '';
};

const validateForm = () => {
  errors.email = '';
  errors.password = '';

  if (!form.email) {
    errors.email = 'Email is required';
    return false;
  }

  if (!isValidEmail(form.email)) {
    errors.email = 'Invalid email format';
    return false;
  }

  if (!form.password) {
    errors.password = 'Password is required';
    return false;
  }

  return true;
};

const handleLogin = async () => {
  if (!validateForm()) return;

  loading.value = true;

  try {
    const response = await login({
      email: form.email,
      password: form.password,
    });

    // Check if email is verified
    if (response.user && !response.user.emailVerified) {
      toast.warning('Please verify your email address to continue. Check your inbox.');
      // Still allow login but show warning
    }

    toast.success('Login successful!');

    // Redirect to intended page or dashboard
    const redirect = route.query.redirect as string;
    await router.push(redirect || '/dashboard/todos');
  } catch (error: any) {
    console.error('Login error:', error);

    if (error.message?.includes('email') && error.message?.includes('verified')) {
      toast.error('Please verify your email address before logging in.');
    } else if (error.message?.includes('credentials') || error.message?.includes('Invalid')) {
      toast.error('Invalid email or password');
    } else {
      toast.error(error.message || 'Login failed. Please try again.');
    }
  } finally {
    loading.value = false;
  }
};

definePageMeta({
  middleware: 'guest',
});
</script>
