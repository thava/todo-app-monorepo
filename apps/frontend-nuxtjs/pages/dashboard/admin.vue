<template>
  <div class="max-w-7xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-foreground">Admin Panel</h1>
      <p class="text-muted mt-1">Manage users and system settings</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-foreground">{{ users.length }}</div>
        <div class="text-sm text-muted">Total Users</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-primary-600">{{ verifiedUsers }}</div>
        <div class="text-sm text-muted">Verified</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-warning-600">{{ adminUsers }}</div>
        <div class="text-sm text-muted">Admins</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-error-600">{{ sysadminUsers }}</div>
        <div class="text-sm text-muted">Sysadmins</div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-surface-primary rounded-lg border border-border overflow-hidden">
      <div class="p-6 border-b border-border">
        <h2 class="text-xl font-semibold text-foreground">Users</h2>
      </div>

      <LoadingSpinner v-if="loading" center text="Loading users..." class="py-12" />

      <div v-else-if="users.length === 0" class="text-center py-12">
        <p class="text-muted">No users found</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-border">
          <thead class="bg-surface-secondary">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
                Joined
              </th>
              <th v-if="isSysAdmin" class="px-6 py-3 text-right text-xs font-medium text-muted uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="user in users"
              :key="user.id"
              class="hover:bg-surface-secondary transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <div class="text-sm font-medium text-foreground">{{ user.fullName }}</div>
                  <div class="text-sm text-muted">{{ user.email }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium"
                  :class="getRoleClass(user.role)"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="user.emailVerified"
                  class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300"
                >
                  ✓ Verified
                </span>
                <span
                  v-else
                  class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300"
                >
                  ! Unverified
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-muted">
                {{ formatDate(user.createdAt) }}
              </td>
              <td v-if="isSysAdmin" class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button
                  v-if="user.id !== currentUser?.id"
                  @click="confirmDeleteUser(user.id, user.fullName)"
                  class="text-error-600 hover:text-error-700 dark:text-error-400 dark:hover:text-error-300"
                >
                  Delete
                </button>
                <span v-else class="text-muted italic">You</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :isOpen="deleteDialog.isOpen"
      :title="`Delete User`"
      :message="`Are you sure you want to delete ${deleteDialog.userName}? This action cannot be undone.`"
      confirmText="Delete"
      cancelText="Cancel"
      variant="danger"
      :loading="deleting"
      @confirm="handleDeleteUser"
      @cancel="deleteDialog.isOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types';

const { user: currentUser, isSysAdmin } = useAuth();
const api = useApi();
const toast = useToast();
const { formatDate } = useUtils();

const loading = ref(false);
const deleting = ref(false);
const users = ref<User[]>([]);

const deleteDialog = reactive({
  isOpen: false,
  userId: null as string | null,
  userName: '',
});

const verifiedUsers = computed(() => users.value.filter((u) => u.emailVerified).length);
const adminUsers = computed(() => users.value.filter((u) => u.role === 'admin').length);
const sysadminUsers = computed(() => users.value.filter((u) => u.role === 'sysadmin').length);

const getRoleClass = (role: string) => {
  switch (role) {
    case 'sysadmin':
      return 'bg-error-100 text-error-700 dark:bg-error-900 dark:text-error-300';
    case 'admin':
      return 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300';
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
  }
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    users.value = await api.getUsers();
  } catch (error: any) {
    toast.error(error.message || 'Failed to load users');
  } finally {
    loading.value = false;
  }
};

const confirmDeleteUser = (userId: string, userName: string) => {
  deleteDialog.userId = userId;
  deleteDialog.userName = userName;
  deleteDialog.isOpen = true;
};

const handleDeleteUser = async () => {
  if (!deleteDialog.userId) return;

  deleting.value = true;
  try {
    await api.deleteUser(deleteDialog.userId);
    users.value = users.value.filter((u) => u.id !== deleteDialog.userId);
    toast.success('User deleted successfully');
    deleteDialog.isOpen = false;
    deleteDialog.userId = null;
    deleteDialog.userName = '';
  } catch (error: any) {
    toast.error(error.message || 'Failed to delete user');
  } finally {
    deleting.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});

definePageMeta({
  middleware: 'admin',
});
</script>
