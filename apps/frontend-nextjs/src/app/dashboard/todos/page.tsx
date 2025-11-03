"use client";

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

interface Todo {
  id: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string | null;
  createdAt: string;
  updatedAt: string;
  ownerId: string;
  ownerEmail?: string;
  ownerName?: string;
  ownerRole?: 'guest' | 'admin' | 'sysadmin';
}

export default function TodosPage() {
  const { accessToken, user: currentUser } = useAuthStore();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; todoId: string | null }>({
    isOpen: false,
    todoId: null,
  });
  const [recentlyUpdatedId, setRecentlyUpdatedId] = useState<string | null>(null);

  // Form state
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState('');

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError('');
    try {
      const data = await api.getTodos(accessToken) as Todo[];
      setTodos(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load todos');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;

    setError(''); // Clear any existing errors
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

    setError(''); // Clear any existing errors
    try {
      const updatedTodo = await api.updateTodo(accessToken, editingTodo.id, {
        description,
        priority,
        dueDate: dueDate || undefined,
      }) as Todo;
      setTodos(todos.map((t) => (t.id === editingTodo.id ? updatedTodo : t)));

      const updatedTodoId = editingTodo.id;

      // Show "Updated" badge temporarily
      setRecentlyUpdatedId(updatedTodoId);
      setTimeout(() => {
        setRecentlyUpdatedId(null);
      }, 3000); // Badge disappears after 3 seconds

      resetForm();

      // Scroll to center the updated todo item
      setTimeout(() => {
        const element = document.getElementById(`todo-${updatedTodoId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
    } catch (err: any) {
      setError(err?.message || 'Failed to update todo');
      // Scroll to top to show error message (accounts for fixed navbar)
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 50);
    }
  };

  const handleDeleteClick = (id: string) => {
    setDeleteConfirm({ isOpen: true, todoId: id });
  };

  const handleDeleteConfirm = async () => {
    if (!accessToken || !deleteConfirm.todoId) return;

    setError(''); // Clear any existing errors
    try {
      await api.deleteTodo(accessToken, deleteConfirm.todoId);
      setTodos(todos.filter((t) => t.id !== deleteConfirm.todoId));
      setDeleteConfirm({ isOpen: false, todoId: null });
    } catch (err: any) {
      setError(err?.message || 'Failed to delete todo');
      setDeleteConfirm({ isOpen: false, todoId: null });
      // Scroll to top to show error message (accounts for fixed navbar)
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 50);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ isOpen: false, todoId: null });
  };

  const startEdit = (todo: Todo) => {
    setError(''); // Clear errors when starting edit
    setShowForm(false); // Close create form if open
    setEditingTodo(todo);
    setDescription(todo.description);
    setPriority(todo.priority);
    setDueDate(todo.dueDate ? todo.dueDate.split('T')[0] : '');
  };

  const resetForm = () => {
    setDescription('');
    setPriority('medium');
    setDueDate('');
    setEditingTodo(null);
    setShowForm(false);
    setError(''); // Clear errors when closing form
  };

  const cancelEdit = () => {
    setEditingTodo(null);
    setDescription('');
    setPriority('medium');
    setDueDate('');
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

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'sysadmin':
        return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      case 'admin':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'guest':
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
      default:
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
    }
  };

  const canEditOrDelete = (todo: Todo) => {
    if (!currentUser) return false;
    // Sysadmin can edit/delete all todos
    if (currentUser.role === 'sysadmin') return true;
    // Others can only edit/delete their own todos
    return todo.ownerId === currentUser.id;
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold text-foreground">My Todos</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
        >
          {showForm ? 'Cancel' : 'New Todo'}
        </button>
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
              id={`todo-${todo.id}`}
              className={`bg-surface-primary rounded-xl shadow-md border border-border p-6 hover:shadow-lg transition-all duration-300 ${
                recentlyUpdatedId === todo.id ? 'ring-4 ring-green-400 dark:ring-green-500 shadow-2xl' : ''
              }`}
            >
              {editingTodo?.id === todo.id ? (
                // Inline Edit Form
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-4">Edit Todo</h3>
                  <form onSubmit={handleUpdateTodo} className="space-y-4">
                    <div>
                      <label htmlFor={`description-${todo.id}`} className="block text-sm font-medium text-foreground mb-2">
                        Description *
                      </label>
                      <textarea
                        id={`description-${todo.id}`}
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
                        <label htmlFor={`priority-${todo.id}`} className="block text-sm font-medium text-foreground mb-2">
                          Priority
                        </label>
                        <select
                          id={`priority-${todo.id}`}
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
                        <label htmlFor={`dueDate-${todo.id}`} className="block text-sm font-medium text-foreground mb-2">
                          Due Date (Optional)
                        </label>
                        <input
                          id={`dueDate-${todo.id}`}
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
                        Update Todo
                      </button>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className="px-4 py-2 bg-surface-primary hover:bg-surface-secondary border border-border text-foreground font-medium rounded-lg shadow-sm transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                // Todo Display
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-lg text-foreground mb-3">{todo.description}</p>

                    {/* Owner Information - only show if todo owner is different from current user */}
                    {todo.ownerId !== currentUser?.id && todo.ownerName && (
                      <div className="mb-3 p-3 bg-surface-secondary rounded-lg border border-border">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium text-foreground">Owner:</span>
                          <span className="text-sm text-foreground">{todo.ownerName}</span>
                          <span className="text-sm text-muted">({todo.ownerEmail})</span>
                          {todo.ownerRole && (
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(todo.ownerRole)}`}>
                              {todo.ownerRole}
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center gap-4 text-sm flex-wrap">
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
                  <div className="flex flex-col gap-2 ml-4 items-end">
                    {canEditOrDelete(todo) && (
                      <div className="flex gap-2">
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
                    )}
                    {recentlyUpdatedId === todo.id && (
                      <span className="px-3 py-1.5 rounded-lg font-semibold text-sm bg-green-500 dark:bg-green-600 text-white shadow-lg animate-bounce">
                        ✓ Updated
                      </span>
                    )}
                  </div>
                </div>
              )}
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
