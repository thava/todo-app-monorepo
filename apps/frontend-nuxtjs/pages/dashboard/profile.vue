<template>
  <div class="max-w-4xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-foreground">Profile</h1>
      <p class="text-muted mt-1">Manage your account information</p>
    </div>

    <!-- Profile Information -->
    <div class="bg-surface-primary p-6 rounded-lg border border-border mb-6">
      <h2 class="text-xl font-semibold text-foreground mb-4">Personal Information</h2>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Email</label>
          <div class="flex items-center gap-2">
            <Input
              :modelValue="user?.email"
              disabled
              class="flex-1"
            />
            <span
              v-if="user?.emailVerified"
              class="inline-flex items-center px-3 py-1 rounded text-sm font-medium bg-success-50 text-success-600 dark:bg-success-900 dark:text-success-300"
            >
              ✓ Verified
            </span>
            <span
              v-else
              class="inline-flex items-center px-3 py-1 rounded text-sm font-medium bg-warning-50 text-warning-600 dark:bg-warning-900 dark:text-warning-300"
            >
              ! Unverified
            </span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Role</label>
          <Input
            :modelValue="user?.role"
            disabled
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-foreground mb-1">Member Since</label>
          <Input
            :modelValue="formatDate(user?.createdAt)"
            disabled
          />
        </div>
      </div>
    </div>

    <!-- Edit Profile -->
    <div class="bg-surface-primary p-6 rounded-lg border border-border">
      <h2 class="text-xl font-semibold text-foreground mb-4">Edit Profile</h2>

      <form @submit.prevent="handleUpdateProfile" class="space-y-6">
        <Input
          id="fullName"
          v-model="form.fullName"
          label="Full Name"
          placeholder="John Doe"
          required
          :error="errors.fullName"
        />

        <div class="flex gap-4">
          <Button
            type="submit"
            :loading="updating"
            :disabled="updating"
          >
            Save Changes
          </Button>
          <Button
            type="button"
            variant="secondary"
            @click="resetForm"
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>

    <!-- Account Stats -->
    <div class="mt-6 bg-surface-primary p-6 rounded-lg border border-border">
      <h2 class="text-xl font-semibold text-foreground mb-4">Account Statistics</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="text-center p-4 bg-surface-secondary rounded-lg">
          <div class="text-2xl font-bold text-primary-600">{{ todosStore.todos.length }}</div>
          <div class="text-sm text-muted">Total Todos</div>
        </div>
        <div class="text-center p-4 bg-surface-secondary rounded-lg">
          <div class="text-2xl font-bold text-success-600">{{ todosStore.completedTodos.length }}</div>
          <div class="text-sm text-muted">Completed</div>
        </div>
        <div class="text-center p-4 bg-surface-secondary rounded-lg">
          <div class="text-2xl font-bold text-warning-600">{{ todosStore.pendingTodos.length }}</div>
          <div class="text-sm text-muted">Pending</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, updateProfile } = useAuth();
const todosStore = useTodosStore();
const toast = useToast();
const { formatDate } = useUtils();

const updating = ref(false);

const form = reactive({
  fullName: user.value?.fullName || '',
});

const errors = reactive({
  fullName: '',
});

// Watch for user changes
watch(user, (newUser) => {
  if (newUser) {
    form.fullName = newUser.fullName;
  }
});

const validateForm = () => {
  errors.fullName = '';

  if (!form.fullName.trim()) {
    errors.fullName = 'Full name is required';
    return false;
  }

  return true;
};

const handleUpdateProfile = async () => {
  if (!validateForm()) return;

  updating.value = true;
  try {
    await updateProfile({ fullName: form.fullName });
    toast.success('Profile updated successfully!');
  } catch (error: any) {
    toast.error(error.message || 'Failed to update profile');
  } finally {
    updating.value = false;
  }
};

const resetForm = () => {
  form.fullName = user.value?.fullName || '';
  errors.fullName = '';
};

// Load todos if not already loaded
onMounted(async () => {
  if (todosStore.todos.length === 0) {
    try {
      await todosStore.fetchTodos();
    } catch (error) {
      // Silently fail - stats will just show 0
    }
  }
});

definePageMeta({
  middleware: 'auth',
});
</script>
