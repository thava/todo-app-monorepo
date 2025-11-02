import React from 'react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-surface-primary">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-muted">
            <span className="text-xl">✓</span>
            <span className="text-sm">
              © {currentYear} TodoGizmo. All rights reserved.
            </span>
          </div>

          <div className="flex gap-6 text-sm text-muted">
            <a href="/about" className="hover:text-primary-600 transition-colors no-underline">
              About
            </a>
            <a href="#" className="hover:text-primary-600 transition-colors no-underline">
              Privacy
            </a>
            <a href="#" className="hover:text-primary-600 transition-colors no-underline">
              Terms
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
