<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
        @click.self="handleCancel"
      >
        <div class="bg-surface-primary rounded-lg shadow-xl max-w-md w-full p-6">
          <!-- Icon -->
          <div
            class="mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4"
            :class="iconBgClass"
          >
            <svg
              class="h-6 w-6"
              :class="iconColorClass"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                v-if="variant === 'danger'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          <!-- Title -->
          <h3 class="text-lg font-medium text-foreground text-center mb-2">
            {{ title }}
          </h3>

          <!-- Message -->
          <p class="text-sm text-muted text-center mb-6">
            {{ message }}
          </p>

          <!-- Actions -->
          <div class="flex space-x-3">
            <Button
              variant="secondary"
              class="flex-1"
              @click="handleCancel"
            >
              {{ cancelText }}
            </Button>
            <Button
              :variant="variant === 'danger' ? 'danger' : 'primary'"
              class="flex-1"
              :loading="loading"
              @click="handleConfirm"
            >
              {{ confirmText }}
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'info';
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  variant: 'info',
  loading: false,
});

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();

const handleConfirm = () => {
  emit('confirm');
};

const handleCancel = () => {
  emit('cancel');
};

const iconBgClass = computed(() => {
  return props.variant === 'danger'
    ? 'bg-error-100 dark:bg-error-900'
    : 'bg-primary-100 dark:bg-primary-900';
});

const iconColorClass = computed(() => {
  return props.variant === 'danger'
    ? 'text-error-600 dark:text-error-400'
    : 'text-primary-600 dark:text-primary-400';
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
