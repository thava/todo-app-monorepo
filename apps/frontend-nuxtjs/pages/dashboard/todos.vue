<template>
  <div class="max-w-6xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-foreground">My Todos</h1>
      <p class="text-muted mt-1">Manage your tasks efficiently</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-foreground">{{ todosStore.todos.length }}</div>
        <div class="text-sm text-muted">Total</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-primary-600">{{ todosStore.pendingTodos.length }}</div>
        <div class="text-sm text-muted">Pending</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-success-600">{{ todosStore.completedTodos.length }}</div>
        <div class="text-sm text-muted">Completed</div>
      </div>
      <div class="bg-surface-primary p-4 rounded-lg border border-border">
        <div class="text-2xl font-bold text-error-600">{{ todosStore.overdueTodos.length }}</div>
        <div class="text-sm text-muted">Overdue</div>
      </div>
    </div>

    <!-- Add Todo Form -->
    <div class="bg-surface-primary p-6 rounded-lg border border-border mb-6">
      <h2 class="text-lg font-semibold text-foreground mb-4">Add New Todo</h2>
      <form @submit.prevent="handleAddTodo" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <Input
              v-model="newTodo.description"
              placeholder="What needs to be done?"
              required
            />
          </div>
          <div>
            <select
              v-model="newTodo.priority"
              class="block w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-foreground"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
          </div>
        </div>
        <div class="flex gap-4">
          <Input
            v-model="newTodo.dueDate"
            type="date"
            placeholder="Due date (optional)"
          />
          <Button type="submit" :loading="adding">
            Add Todo
          </Button>
        </div>
      </form>
    </div>

    <!-- Todos List -->
    <div class="space-y-3">
      <LoadingSpinner v-if="loading" center text="Loading todos..." />

      <div v-else-if="todosStore.todos.length === 0" class="text-center py-12 bg-surface-primary rounded-lg border border-border">
        <svg class="mx-auto h-12 w-12 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="mt-4 text-muted">No todos yet. Create one to get started!</p>
      </div>

      <div
        v-for="todo in sortedTodos"
        :key="todo.id"
        class="bg-surface-primary p-4 rounded-lg border border-border hover:shadow-md transition-shadow"
      >
        <!-- View Mode -->
        <div v-if="editingId !== todo.id" class="flex items-start gap-4">
          <!-- Checkbox -->
          <button
            @click="handleToggleTodo(todo.id)"
            class="mt-1 flex-shrink-0"
          >
            <div
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-colors"
              :class="todo.completed ? 'bg-success-600 border-success-600' : 'border-gray-300 dark:border-gray-600'"
            >
              <svg v-if="todo.completed" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </button>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p
              class="text-foreground"
              :class="{ 'line-through text-muted': todo.completed }"
            >
              {{ todo.description }}
            </p>
            <div class="flex flex-wrap items-center gap-3 mt-2 text-sm">
              <span
                v-if="todo.priority"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="priorityClass(todo.priority)"
              >
                {{ todo.priority }}
              </span>
              <span v-if="todo.dueDate" class="text-muted flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(todo.dueDate) }}
                <span v-if="isPastDue(todo.dueDate) && !todo.completed" class="text-error-500">(Overdue)</span>
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              @click="startEditing(todo)"
              class="p-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 rounded"
              title="Edit"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="confirmDelete(todo.id)"
              class="p-2 text-gray-600 dark:text-gray-400 hover:text-error-600 dark:hover:text-error-400 rounded"
              title="Delete"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Edit Mode (Inline) -->
        <div v-else class="space-y-4">
          <Input
            v-model="editForm.description"
            placeholder="What needs to be done?"
            required
          />
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select
              v-model="editForm.priority"
              class="block w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-foreground"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <Input
              v-model="editForm.dueDate"
              type="date"
            />
          </div>
          <div class="flex gap-2">
            <Button @click="handleUpdateTodo" :loading="updating">
              Save
            </Button>
            <Button variant="secondary" @click="cancelEditing">
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :isOpen="deleteDialog.isOpen"
      title="Delete Todo"
      message="Are you sure you want to delete this todo? This action cannot be undone."
      confirmText="Delete"
      cancelText="Cancel"
      variant="danger"
      :loading="deleting"
      @confirm="handleDeleteTodo"
      @cancel="deleteDialog.isOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import type { Todo } from '~/types';

const todosStore = useTodosStore();
const toast = useToast();
const { formatDate, isPastDue } = useUtils();

const loading = ref(false);
const adding = ref(false);
const updating = ref(false);
const deleting = ref(false);

const editingId = ref<string | null>(null);

const newTodo = reactive({
  description: '',
  priority: 'medium' as 'low' | 'medium' | 'high',
  dueDate: '',
});

const editForm = reactive({
  description: '',
  priority: 'medium' as 'low' | 'medium' | 'high',
  dueDate: '',
});

const deleteDialog = reactive({
  isOpen: false,
  todoId: null as string | null,
});

const sortedTodos = computed(() => {
  return [...todosStore.todos].sort((a, b) => {
    // Incomplete first
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    // Then by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    const aPriority = priorityOrder[a.priority || 'low'];
    const bPriority = priorityOrder[b.priority || 'low'];
    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }
    // Then by due date
    if (a.dueDate && b.dueDate) {
      return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
    }
    return 0;
  });
});

const priorityClass = (priority?: string) => {
  switch (priority) {
    case 'high':
      return 'bg-error-100 text-error-700 dark:bg-error-900 dark:text-error-300';
    case 'medium':
      return 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300';
    case 'low':
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
  }
};

const handleAddTodo = async () => {
  adding.value = true;
  try {
    await todosStore.createTodo({
      description: newTodo.description,
      priority: newTodo.priority,
      dueDate: newTodo.dueDate || undefined,
    });

    toast.success('Todo added successfully!');

    // Reset form
    newTodo.description = '';
    newTodo.priority = 'medium';
    newTodo.dueDate = '';
  } catch (error: any) {
    toast.error(error.message || 'Failed to add todo');
  } finally {
    adding.value = false;
  }
};

const handleToggleTodo = async (id: string) => {
  try {
    await todosStore.toggleTodo(id);
  } catch (error: any) {
    toast.error(error.message || 'Failed to update todo');
  }
};

const startEditing = (todo: Todo) => {
  editingId.value = todo.id;
  editForm.description = todo.description;
  editForm.priority = todo.priority || 'medium';
  editForm.dueDate = formatDateForInput(todo.dueDate);
};

const cancelEditing = () => {
  editingId.value = null;
};

const handleUpdateTodo = async () => {
  if (!editingId.value) return;

  updating.value = true;
  try {
    await todosStore.updateTodo(editingId.value, {
      description: editForm.description,
      priority: editForm.priority,
      dueDate: editForm.dueDate || null,
    });

    toast.success('Todo updated successfully!');
    editingId.value = null;
  } catch (error: any) {
    toast.error(error.message || 'Failed to update todo');
  } finally {
    updating.value = false;
  }
};

const confirmDelete = (id: string) => {
  deleteDialog.todoId = id;
  deleteDialog.isOpen = true;
};

const handleDeleteTodo = async () => {
  if (!deleteDialog.todoId) return;

  deleting.value = true;
  try {
    await todosStore.deleteTodo(deleteDialog.todoId);
    toast.success('Todo deleted successfully!');
    deleteDialog.isOpen = false;
    deleteDialog.todoId = null;
  } catch (error: any) {
    toast.error(error.message || 'Failed to delete todo');
  } finally {
    deleting.value = false;
  }
};

// Fetch todos on mount
onMounted(async () => {
  loading.value = true;
  try {
    await todosStore.fetchTodos();
  } catch (error: any) {
    toast.error(error.message || 'Failed to load todos');
  } finally {
    loading.value = false;
  }
});

definePageMeta({
  middleware: 'auth',
});
</script>
