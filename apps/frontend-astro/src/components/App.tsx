import React from 'react';
import { ThemeProvider } from './theme/ThemeProvider';
import { AuthProvider } from './auth/AuthProvider';
import { TopBar } from './layout/TopBar';
import { Footer } from './layout/Footer';

interface AppProps {
  children: React.ReactNode;
}

export function App({ children }: AppProps) {
  return (
    <ThemeProvider defaultTheme="system" storageKey="todogizmo-theme">
      <AuthProvider>
        <div className="flex flex-col min-h-screen">
          <TopBar />
          <main className="flex-1 pt-16">
            {children}
          </main>
          <Footer />
        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}
