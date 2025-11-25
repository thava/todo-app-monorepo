<template>
  <div :class="containerClasses">
    <svg
      class="animate-spin"
      :class="sizeClasses"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    <span v-if="text" :class="textClasses">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  center?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  center: false,
});

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };
  return `${sizes[props.size]} text-primary-600`;
});

const containerClasses = computed(() => {
  const base = 'flex items-center gap-2';
  return props.center ? `${base} justify-center` : base;
});

const textClasses = computed(() => {
  return 'text-sm text-muted';
});
</script>
