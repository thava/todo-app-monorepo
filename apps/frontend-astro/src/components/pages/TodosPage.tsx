import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../lib/store';
import { api } from '../../lib/api';
import { ConfirmDialog } from '../ui/ConfirmDialog';

interface Todo {
  id: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export function TodosPage() {
  const { accessToken, isAuthenticated, _hasHydrated } = useAuthStore();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; todoId: string | null }>({
    isOpen: false,
    todoId: null,
  });

  // Form state
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState('');

  // Load todos when auth is ready
  useEffect(() => {
    if (_hasHydrated && isAuthenticated && accessToken) {
      loadTodos();
    } else if (_hasHydrated && !isAuthenticated) {
      // Not authenticated, redirect to login
      window.location.href = '/login';
    }
  }, [_hasHydrated, isAuthenticated, accessToken]);

  const loadTodos = async () => {
    if (!accessToken) {
      console.error('No access token available');
      setError('Not authenticated. Please login again.');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      console.log('Fetching todos with token:', accessToken.substring(0, 20) + '...');
      const data = await api.getTodos(accessToken) as Todo[];
      console.log('Todos loaded:', data);
      setTodos(data);
    } catch (err: any) {
      console.error('Error loading todos:', err);
      setError(err?.message || 'Failed to load todos');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;

    setError('');
    try {
      const newTodo = await api.createTodo(accessToken, {
        description,
        priority,
        dueDate: dueDate || undefined,
      }) as Todo;
      setTodos([newTodo, ...todos]);
      resetForm();
    } catch (err: any) {
      setError(err?.message || 'Failed to create todo');
    }
  };

  const handleUpdateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !editingTodo) return;

    setError('');
    try {
      const updatedTodo = await api.updateTodo(accessToken, editingTodo.id, {
        description,
        priority,
        dueDate: dueDate || undefined,
      }) as Todo;
      setTodos(todos.map((t) => (t.id === editingTodo.id ? updatedTodo : t)));
      resetForm();
    } catch (err: any) {
      setError(err?.message || 'Failed to update todo');
    }
  };

  const handleDeleteClick = (id: string) => {
    setDeleteConfirm({ isOpen: true, todoId: id });
  };

  const handleDeleteConfirm = async () => {
    if (!accessToken || !deleteConfirm.todoId) return;

    setError('');
    try {
      await api.deleteTodo(accessToken, deleteConfirm.todoId);
      setTodos(todos.filter((t) => t.id !== deleteConfirm.todoId));
      setDeleteConfirm({ isOpen: false, todoId: null });
    } catch (err: any) {
      setError(err?.message || 'Failed to delete todo');
      setDeleteConfirm({ isOpen: false, todoId: null });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ isOpen: false, todoId: null });
  };

  const startEdit = (todo: Todo) => {
    setError('');
    setEditingTodo(todo);
    setDescription(todo.description);
    setPriority(todo.priority);
    setDueDate(todo.dueDate ? todo.dueDate.split('T')[0] : '');
    setShowForm(true);
  };

  const resetForm = () => {
    setDescription('');
    setPriority('medium');
    setDueDate('');
    setEditingTodo(null);
    setShowForm(false);
    setError('');
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      case 'medium':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      default:
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
    }
  };

  // Show loading while auth is being checked
  if (!_hasHydrated) {
    return (
      <div className="text-center py-12 text-muted">Loading...</div>
    );
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold text-foreground">My Todos</h1>
        <div className="flex gap-2">
          <button
            onClick={loadTodos}
            disabled={isLoading}
            className="px-4 py-2 bg-surface-primary hover:bg-surface-secondary border border-border text-foreground font-medium rounded-lg shadow-sm transition-colors disabled:opacity-50"
            title="Refresh todos"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
          >
            {showForm ? 'Cancel' : 'New Todo'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start justify-between">
          <p className="text-sm text-red-600 dark:text-red-400 flex-1">{error}</p>
          <button
            onClick={() => setError('')}
            className="ml-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
            aria-label="Dismiss error"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {showForm && (
        <div className="mb-8 bg-surface-primary rounded-xl shadow-md border border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">
            {editingTodo ? 'Edit Todo' : 'Create New Todo'}
          </h2>
          <form onSubmit={editingTodo ? handleUpdateTodo : handleCreateTodo} className="space-y-4">
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-foreground mb-2">
                Description *
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                rows={3}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter todo description..."
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-foreground mb-2">
                  Priority
                </label>
                <select
                  id="priority"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label htmlFor="dueDate" className="block text-sm font-medium text-foreground mb-2">
                  Due Date (Optional)
                </label>
                <input
                  id="dueDate"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
              >
                {editingTodo ? 'Update Todo' : 'Create Todo'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 bg-surface-primary hover:bg-surface-secondary border border-border text-foreground font-medium rounded-lg shadow-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12 text-muted">Loading todos...</div>
      ) : todos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted mb-4">No todos yet. Create your first one!</p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
          >
            Create Todo
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {todos.map((todo) => (
            <div
              key={todo.id}
              className="bg-surface-primary rounded-xl shadow-md border border-border p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-lg text-foreground mb-2">{todo.description}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className={`px-2 py-1 rounded-full font-medium ${getPriorityColor(todo.priority)}`}>
                      {todo.priority}
                    </span>
                    {todo.dueDate && (
                      <span className="text-muted">
                        Due: {new Date(todo.dueDate).toLocaleDateString()}
                      </span>
                    )}
                    <span className="text-muted">
                      Created: {new Date(todo.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => startEdit(todo)}
                    className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-800 dark:text-blue-200 rounded-lg transition-colors shadow-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteClick(todo.id)}
                    className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 text-red-800 dark:text-red-200 rounded-lg transition-colors shadow-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Delete Todo"
        message="Are you sure you want to delete this todo? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}
