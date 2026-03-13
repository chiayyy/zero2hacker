import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import AnimatedBackground from '../ui/AnimatedBackground';
import AIChatbot from '../AIChatbot';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { id } = useParams<{ id: string }>();

  // Extract challenge ID from URL if on challenge detail page
  const challengeId = id ? parseInt(id) : undefined;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900 relative">
      {/* Animated background */}
      <AnimatedBackground particleCount={50} enableMouseGlow={true} />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <motion.div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="lg:pl-64 relative z-10">
        {/* Navbar */}
        <Navbar onMenuClick={() => setSidebarOpen(true)} />

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            <motion.div
              className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>

      {/* AI Chatbot - available on all pages */}
      <AIChatbot challengeId={challengeId} />
    </div>
  );
};

export default Layout;