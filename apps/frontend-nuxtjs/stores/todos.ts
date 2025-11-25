import { defineStore } from 'pinia';
import type { Todo, CreateTodoDto, UpdateTodoDto } from '~/types';

interface TodosState {
  todos: Todo[];
  loading: boolean;
  error: string | null;
}

export const useTodosStore = defineStore('todos', {
  state: (): TodosState => ({
    todos: [],
    loading: false,
    error: null,
  }),

  getters: {
    completedTodos: (state) => state.todos.filter((todo) => todo.completed),
    pendingTodos: (state) => state.todos.filter((todo) => !todo.completed),

    todosByPriority: (state) => (priority: string) =>
      state.todos.filter((todo) => todo.priority === priority),

    overdueTodos: (state) => {
      const now = new Date();
      return state.todos.filter(
        (todo) => !todo.completed && todo.dueDate && new Date(todo.dueDate) < now
      );
    },
  },

  actions: {
    /**
     * Fetch all todos
     */
    async fetchTodos() {
      this.loading = true;
      this.error = null;

      try {
        const api = useApi();
        const todos = await api.getTodos();
        this.todos = todos;
      } catch (error: any) {
        console.error('Fetch todos error:', error);
        this.error = error.message || 'Failed to fetch todos';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Create a new todo
     */
    async createTodo(data: CreateTodoDto) {
      try {
        const api = useApi();
        const todo = await api.createTodo(data);
        this.todos.push(todo);
        return todo;
      } catch (error: any) {
        console.error('Create todo error:', error);
        throw error;
      }
    },

    /**
     * Update a todo
     */
    async updateTodo(id: string, data: UpdateTodoDto) {
      try {
        const api = useApi();
        const updatedTodo = await api.updateTodo(id, data);

        const index = this.todos.findIndex((t) => t.id === id);
        if (index > -1) {
          this.todos[index] = updatedTodo;
        }

        return updatedTodo;
      } catch (error: any) {
        console.error('Update todo error:', error);
        throw error;
      }
    },

    /**
     * Toggle todo completion status
     */
    async toggleTodo(id: string) {
      const todo = this.todos.find((t) => t.id === id);
      if (!todo) return;

      const completed = !todo.completed;
      return this.updateTodo(id, { completed });
    },

    /**
     * Delete a todo
     */
    async deleteTodo(id: string) {
      try {
        const api = useApi();
        await api.deleteTodo(id);

        const index = this.todos.findIndex((t) => t.id === id);
        if (index > -1) {
          this.todos.splice(index, 1);
        }
      } catch (error: any) {
        console.error('Delete todo error:', error);
        throw error;
      }
    },

    /**
     * Clear all todos (local state only)
     */
    clearTodos() {
      this.todos = [];
      this.error = null;
    },
  },
});
