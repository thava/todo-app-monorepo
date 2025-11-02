"use client";

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'guest' | 'admin' | 'sysadmin';
  emailVerified: boolean;
  emailVerifiedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

interface EditableFields {
  fullName: boolean;
  email: boolean;
  role: boolean;
  password: boolean;
  emailVerifiedAt: boolean;
}

export default function AdminPage() {
  const { accessToken, user: currentUser } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; userId: string | null }>({
    isOpen: false,
    userId: null,
  });

  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'guest' | 'admin' | 'sysadmin'>('guest');
  const [password, setPassword] = useState('');
  const [emailVerifiedAt, setEmailVerifiedAt] = useState<'keep' | 'null' | 'now'>('keep');
  const [editableFields, setEditableFields] = useState<EditableFields>({
    fullName: false,
    email: false,
    role: false,
    password: false,
    emailVerifiedAt: false,
  });

  // Create user form state
  const [createFullName, setCreateFullName] = useState('');
  const [createEmail, setCreateEmail] = useState('');
  const [createPassword, setCreatePassword] = useState('');
  const [createRole, setCreateRole] = useState<'guest' | 'admin' | 'sysadmin'>('guest');
  const [createAutoVerify, setCreateAutoVerify] = useState(false);

  const isSysadmin = currentUser?.role === 'sysadmin';
  const editFormRef = React.useRef<HTMLDivElement>(null);
  const createFormRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError('');
    try {
      const data = await api.getUsers(accessToken) as User[];
      setUsers(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const startEdit = (user: User) => {
    setError('');
    setShowCreateForm(false); // Close create form if open
    setEditingUser(user);
    setFullName(user.fullName);
    setEmail(user.email);
    setRole(user.role);
    setPassword('');
    setEmailVerifiedAt('keep');
    setEditableFields({
      fullName: false,
      email: false,
      role: false,
      password: false,
      emailVerifiedAt: false,
    });

    // Scroll to top of page to show edit form (accounts for fixed navbar)
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  };

  const resetForm = () => {
    setEditingUser(null);
    setFullName('');
    setEmail('');
    setRole('guest');
    setPassword('');
    setEmailVerifiedAt('keep');
    setEditableFields({
      fullName: false,
      email: false,
      role: false,
      password: false,
      emailVerifiedAt: false,
    });
    setError('');
  };

  const resetCreateForm = () => {
    setShowCreateForm(false);
    setCreateFullName('');
    setCreateEmail('');
    setCreatePassword('');
    setCreateRole('guest');
    setCreateAutoVerify(false);
    setError('');
  };

  const startCreate = () => {
    if (showCreateForm) {
      resetCreateForm();
    } else {
      setError('');
      setShowCreateForm(true);
      setEditingUser(null); // Close edit form if open
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 100);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !isSysadmin) return;

    setError('');

    try {
      const newUser = await api.createUser(accessToken, {
        email: createEmail,
        password: createPassword,
        fullName: createFullName,
        role: createRole,
        autoverify: createAutoVerify,
      }) as { user: User };

      // Reload users list to get the newly created user
      await loadUsers();
      resetCreateForm();
    } catch (err: any) {
      setError(err?.message || 'Failed to create user');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !editingUser || !isSysadmin) return;

    setError('');

    // Build update payload with only edited fields
    const updateData: any = {};
    if (editableFields.fullName) updateData.fullName = fullName;
    if (editableFields.email) updateData.email = email;
    if (editableFields.role) updateData.role = role;
    if (editableFields.password && password) updateData.password = password;
    if (editableFields.emailVerifiedAt) {
      if (emailVerifiedAt === 'null') {
        updateData.emailVerifiedAt = null;
      } else if (emailVerifiedAt === 'now') {
        updateData.emailVerifiedAt = new Date().toISOString();
      }
    }

    // Check if at least one field is being updated
    if (Object.keys(updateData).length === 0) {
      setError('Please select at least one field to update');
      return;
    }

    try {
      const updatedUser = await api.updateUser(accessToken, editingUser.id, updateData) as User;
      setUsers(users.map((u) => (u.id === editingUser.id ? updatedUser : u)));
      resetForm();
    } catch (err: any) {
      setError(err?.message || 'Failed to update user');
    }
  };

  const handleDeleteClick = (id: string) => {
    setDeleteConfirm({ isOpen: true, userId: id });
  };

  const handleDeleteConfirm = async () => {
    if (!accessToken || !deleteConfirm.userId || !isSysadmin) return;

    setError('');
    try {
      await api.deleteUser(accessToken, deleteConfirm.userId);
      setUsers(users.filter((u) => u.id !== deleteConfirm.userId));
      setDeleteConfirm({ isOpen: false, userId: null });
    } catch (err: any) {
      setError(err?.message || 'Failed to delete user');
      setDeleteConfirm({ isOpen: false, userId: null });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ isOpen: false, userId: null });
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

  const toggleField = (field: keyof EditableFields) => {
    setEditableFields((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold text-foreground">User Administration</h1>
        {isSysadmin && (
          <button
            onClick={startCreate}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
          >
            {showCreateForm ? 'Cancel' : 'Create User'}
          </button>
        )}
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

      {showCreateForm && (
        <div ref={createFormRef} className="mb-8 bg-surface-primary rounded-xl shadow-md border border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Create New User</h2>
          <form onSubmit={handleCreateUser} className="space-y-3">
            <div>
              <label htmlFor="create-fullName" className="block text-sm font-medium text-foreground mb-1">
                Full Name *
              </label>
              <input
                id="create-fullName"
                type="text"
                value={createFullName}
                onChange={(e) => setCreateFullName(e.target.value)}
                required
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="create-email" className="block text-sm font-medium text-foreground mb-1">
                Email *
              </label>
              <input
                id="create-email"
                type="email"
                value={createEmail}
                onChange={(e) => setCreateEmail(e.target.value)}
                required
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="create-password" className="block text-sm font-medium text-foreground mb-1">
                Password *
              </label>
              <input
                id="create-password"
                type="password"
                value={createPassword}
                onChange={(e) => setCreatePassword(e.target.value)}
                required
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="create-role" className="block text-sm font-medium text-foreground mb-1">
                Role (Optional)
              </label>
              <select
                id="create-role"
                value={createRole}
                onChange={(e) => setCreateRole(e.target.value as any)}
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="guest">Guest</option>
                <option value="admin">Admin</option>
                <option value="sysadmin">Sysadmin</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                id="create-autoverify"
                type="checkbox"
                checked={createAutoVerify}
                onChange={(e) => setCreateAutoVerify(e.target.checked)}
                className="h-4 w-4 rounded border-border"
              />
              <label htmlFor="create-autoverify" className="text-sm font-medium text-foreground">
                Auto-verify email (Optional)
              </label>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors"
              >
                Create User
              </button>
              <button
                type="button"
                onClick={resetCreateForm}
                className="px-4 py-2 bg-surface-primary hover:bg-surface-secondary border border-border text-foreground font-medium rounded-lg shadow-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {editingUser && (
        <div ref={editFormRef} className="mb-8 bg-surface-primary rounded-xl shadow-md border border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Edit User</h2>
          {!isSysadmin && (
            <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                You need sysadmin privileges to edit users.
              </p>
            </div>
          )}
          <form onSubmit={handleUpdateUser} className="space-y-3">
            {/* Full Name */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="checkbox"
                  id="edit-fullName"
                  checked={editableFields.fullName}
                  onChange={() => toggleField('fullName')}
                  disabled={!isSysadmin}
                  className="h-4 w-4"
                />
                <label htmlFor="fullName" className="text-sm font-medium text-foreground">
                  Full Name
                </label>
              </div>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={!editableFields.fullName || !isSysadmin}
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            {/* Email */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="checkbox"
                  id="edit-email"
                  checked={editableFields.email}
                  onChange={() => toggleField('email')}
                  disabled={!isSysadmin}
                  className="h-4 w-4"
                />
                <label htmlFor="email" className="text-sm font-medium text-foreground">
                  Email
                </label>
              </div>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={!editableFields.email || !isSysadmin}
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            {/* Role */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="checkbox"
                  id="edit-role"
                  checked={editableFields.role}
                  onChange={() => toggleField('role')}
                  disabled={!isSysadmin}
                  className="h-4 w-4"
                />
                <label htmlFor="role" className="text-sm font-medium text-foreground">
                  Role
                </label>
              </div>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as any)}
                disabled={!editableFields.role || !isSysadmin}
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              >
                <option value="guest">Guest</option>
                <option value="admin">Admin</option>
                <option value="sysadmin">Sysadmin</option>
              </select>
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="checkbox"
                  id="edit-password"
                  checked={editableFields.password}
                  onChange={() => toggleField('password')}
                  disabled={!isSysadmin}
                  className="h-4 w-4"
                />
                <label htmlFor="password" className="text-sm font-medium text-foreground">
                  New Password
                </label>
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={!editableFields.password || !isSysadmin}
                placeholder="Leave blank to keep current password"
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            {/* Email Verified At */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="checkbox"
                  id="edit-emailVerifiedAt"
                  checked={editableFields.emailVerifiedAt}
                  onChange={() => toggleField('emailVerifiedAt')}
                  disabled={!isSysadmin}
                  className="h-4 w-4"
                />
                <label htmlFor="emailVerifiedAt" className="text-sm font-medium text-foreground">
                  Email Verified At
                </label>
              </div>
              <div className="text-xs text-muted mb-1">
                Current: {editingUser.emailVerifiedAt
                  ? new Date(editingUser.emailVerifiedAt).toLocaleString()
                  : 'Not verified'}
              </div>
              <select
                id="emailVerifiedAt"
                value={emailVerifiedAt}
                onChange={(e) => setEmailVerifiedAt(e.target.value as any)}
                disabled={!editableFields.emailVerifiedAt || !isSysadmin}
                className="w-full px-3 py-1 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              >
                <option value="keep">Keep current</option>
                <option value="now">Set to now</option>
                <option value="null">Set to null (unverified)</option>
              </select>
            </div>

            <div className="flex gap-2 pt-4">
              <button
                type="submit"
                disabled={!isSysadmin}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Update User
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
        <div className="text-center py-12 text-muted">Loading users...</div>
      ) : users.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted">No users found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="bg-surface-primary rounded-xl shadow-md border border-border p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-foreground">{user.fullName}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                    {user.emailVerified && (
                      <span className="text-green-600 dark:text-green-400 text-xs">✓ Verified</span>
                    )}
                  </div>
                  <p className="text-sm text-muted mb-2">{user.email}</p>
                  <div className="flex items-center gap-4 text-xs text-muted">
                    <span>ID: {user.id}</span>
                    <span>Created: {new Date(user.createdAt).toLocaleDateString()}</span>
                    {user.emailVerifiedAt && (
                      <span>Verified: {new Date(user.emailVerifiedAt).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {isSysadmin && (
                    <>
                      <button
                        onClick={() => startEdit(user)}
                        className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-800 dark:text-blue-200 rounded-lg transition-colors shadow-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteClick(user.id)}
                        className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 text-red-800 dark:text-red-200 rounded-lg transition-colors shadow-sm"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Delete User"
        message="Are you sure you want to delete this user? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}
