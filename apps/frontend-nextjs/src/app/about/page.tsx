"use client";

import React from 'react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 max-w-7xl">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <span className="text-6xl mb-4 block">✓</span>
            <h1 className="text-4xl font-bold text-foreground mb-4">About TodoGizmo</h1>
            <p className="text-xl text-muted">
              Your trusted companion for task management and productivity
            </p>
          </div>

          {/* Mission Section */}
          <div className="bg-surface-primary rounded-xl shadow-md border border-border p-8 mb-8">
            <h2 className="text-2xl font-semibold text-foreground mb-4">Our Mission</h2>
            <p className="text-muted leading-relaxed mb-4">
              TodoGizmo was created with a simple goal: make task management effortless and enjoyable.
              We believe that staying organized should not be complicated or overwhelming.
            </p>
            <p className="text-muted leading-relaxed">
              Our mission is to provide a beautiful, intuitive platform that helps individuals and teams
              manage their tasks efficiently, boost productivity, and achieve their goals without the clutter.
            </p>
          </div>

          {/* Features Section */}
          <div className="bg-surface-primary rounded-xl shadow-md border border-border p-8 mb-8">
            <h2 className="text-2xl font-semibold text-foreground mb-6">What Makes TodoGizmo Special?</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <span className="text-2xl">🎯</span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Simple & Intuitive</h3>
                  <p className="text-muted">
                    No learning curve. Create, manage, and complete tasks with just a few clicks.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="text-2xl">🎨</span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Beautiful Design</h3>
                  <p className="text-muted">
                    Clean, modern interface with light and dark themes that adapt to your preferences.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="text-2xl">⚡</span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Lightning Fast</h3>
                  <p className="text-muted">
                    Built with cutting-edge technology for instant responses and smooth interactions.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="text-2xl">🔒</span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Secure & Private</h3>
                  <p className="text-muted">
                    Your data is encrypted and protected with industry-standard security practices.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <span className="text-2xl">📊</span>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Priority Management</h3>
                  <p className="text-muted">
                    Organize tasks by priority levels and due dates to focus on what matters most.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Technology Section */}
          <div className="bg-surface-primary rounded-xl shadow-md border border-border p-8 mb-8">
            <h2 className="text-2xl font-semibold text-foreground mb-4">Built with Modern Technology</h2>
            <p className="text-muted leading-relaxed mb-4">
              TodoGizmo is built using cutting-edge web technologies to ensure the best performance,
              security, and user experience:
            </p>
            <ul className="space-y-2 text-muted">
              <li className="flex items-center gap-2">
                <span className="text-primary-600">✓</span> Next.js 16 with React 19 for blazing-fast performance
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary-600">✓</span> NestJS backend with PostgreSQL for robust data management
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary-600">✓</span> TypeScript for type-safe, maintainable code
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary-600">✓</span> JWT authentication for secure user sessions
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary-600">✓</span> Responsive design that works on all devices
              </li>
            </ul>
          </div>

          {/* CTA Section */}
          <div className="text-center bg-primary-600 rounded-xl p-8 shadow-lg">
            <h2 className="text-2xl font-bold text-white mb-4">Ready to Get Started?</h2>
            <p className="text-white/90 mb-6">
              Join TodoGizmo today and experience the joy of effortless task management.
            </p>
            <Link
              href="/register"
              className="inline-block px-8 py-3 bg-white hover:bg-gray-100 text-primary-600 font-medium rounded-lg shadow-sm transition-colors no-underline"
            >
              Create Free Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
