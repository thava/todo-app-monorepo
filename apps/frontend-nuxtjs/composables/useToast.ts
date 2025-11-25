/**
 * Composable for toast notifications
 * Provides easy access to toast actions
 */
export const useToast = () => {
  const toastStore = useToastStore();

  return {
    success: (message: string, duration?: number) => toastStore.success(message, duration),
    error: (message: string, duration?: number) => toastStore.error(message, duration),
    warning: (message: string, duration?: number) => toastStore.warning(message, duration),
    info: (message: string, duration?: number) => toastStore.info(message, duration),
    remove: (id: string) => toastStore.remove(id),
    clear: () => toastStore.clear(),
  };
};
