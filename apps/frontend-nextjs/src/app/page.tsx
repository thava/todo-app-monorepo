"use client";

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard/todos');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-background">
      {/* Hero Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-20 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto">
          <div className="mb-6">
            <span className="text-6xl">✓</span>
          </div>
          <h1 className="text-5xl font-bold text-foreground mb-6">
            Welcome to TodoGizmo
          </h1>
          <p className="text-xl text-muted mb-8">
            The beautiful and simple way to manage your tasks. Stay organized, boost productivity, and achieve your goals.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/register"
              className="px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm transition-colors no-underline"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 bg-surface-primary hover:bg-surface-secondary border border-border text-foreground font-medium rounded-lg shadow-sm transition-colors no-underline"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 max-w-7xl">
        <h2 className="text-3xl font-bold text-center text-foreground mb-12">
          Why TodoGizmo?
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
          <div className="text-center p-6 bg-surface-primary rounded-xl border border-border shadow-sm">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold text-foreground mb-2">Fast & Simple</h3>
            <p className="text-muted">
              Create, update, and manage tasks in seconds with our intuitive interface.
            </p>
          </div>
          <div className="text-center p-6 bg-surface-primary rounded-xl border border-border shadow-sm">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-semibold text-foreground mb-2">Beautiful Design</h3>
            <p className="text-muted">
              Enjoy a clean, modern interface with light and dark themes.
            </p>
          </div>
          <div className="text-center p-6 bg-surface-primary rounded-xl border border-border shadow-sm">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold text-foreground mb-2">Secure</h3>
            <p className="text-muted">
              Your data is protected with industry-standard security practices.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 max-w-7xl">
        <div className="max-w-3xl mx-auto text-center bg-primary-600 rounded-xl p-12 shadow-lg">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to get organized?
          </h2>
          <p className="text-white/90 mb-6">
            Join thousands of users who are managing their tasks efficiently with TodoGizmo.
          </p>
          <Link
            href="/register"
            className="inline-block px-8 py-3 bg-white hover:bg-gray-100 text-primary-600 font-medium rounded-lg shadow-sm transition-colors no-underline"
          >
            Start Free Today
          </Link>
        </div>
      </section>
    </div>
  );
}
