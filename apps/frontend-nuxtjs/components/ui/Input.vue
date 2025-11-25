<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-foreground mb-1"
    >
      {{ label }}
      <span v-if="required" class="text-error-500">*</span>
    </label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :class="inputClasses"
      @input="handleInput"
      @blur="emit('blur', $event)"
      @focus="emit('focus', $event)"
    />
    <p v-if="error" class="mt-1 text-sm text-error-500">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-muted">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  id?: string;
  type?: string;
  modelValue?: string | number;
  label?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  hint?: string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
}>();

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

const inputClasses = computed(() => {
  const base = 'block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-0 sm:text-sm transition-colors';

  if (props.error) {
    return `${base} border-error-500 focus:ring-error-500 focus:border-error-500`;
  }

  if (props.disabled) {
    return `${base} border-border bg-gray-100 dark:bg-gray-800 cursor-not-allowed`;
  }

  return `${base} border-border focus:ring-primary-500 focus:border-primary-500 bg-surface-primary text-foreground`;
});
</script>
