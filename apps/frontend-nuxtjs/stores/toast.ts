import { defineStore } from 'pinia';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
}

export const useToastStore = defineStore('toast', {
  state: (): ToastState => ({
    toasts: [],
  }),

  actions: {
    /**
     * Add a toast notification
     */
    add(type: ToastType, message: string, duration: number = 5000) {
      const id = Math.random().toString(36).substring(7);
      const toast: Toast = { id, type, message, duration };

      this.toasts.push(toast);

      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => {
          this.remove(id);
        }, duration);
      }

      return id;
    },

    /**
     * Remove a toast by ID
     */
    remove(id: string) {
      const index = this.toasts.findIndex((t) => t.id === id);
      if (index > -1) {
        this.toasts.splice(index, 1);
      }
    },

    /**
     * Show success toast
     */
    success(message: string, duration?: number) {
      return this.add('success', message, duration);
    },

    /**
     * Show error toast
     */
    error(message: string, duration?: number) {
      return this.add('error', message, duration);
    },

    /**
     * Show warning toast
     */
    warning(message: string, duration?: number) {
      return this.add('warning', message, duration);
    },

    /**
     * Show info toast
     */
    info(message: string, duration?: number) {
      return this.add('info', message, duration);
    },

    /**
     * Clear all toasts
     */
    clear() {
      this.toasts = [];
    },
  },
});
