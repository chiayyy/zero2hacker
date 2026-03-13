import React from 'react';
import { motion } from 'framer-motion';

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Auth form */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Logo */}
            <div className="flex items-center space-x-3 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">Z</span>
              </div>
              <span className="text-2xl font-bold text-gradient">Zero2Hacker</span>
            </div>

            {children}
          </motion.div>
        </div>
      </div>

      {/* Right side - Hero image */}
      <div className="hidden lg:block relative w-0 flex-1">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 to-purple-800">
          <div className="absolute inset-0 bg-black bg-opacity-20"></div>
          <div className="relative h-full flex items-center justify-center p-12">
            <motion.div
              className="text-center text-white"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
            >
              <h2 className="text-4xl font-bold mb-6">
                Master Cybersecurity Through Practice
              </h2>
              <p className="text-xl opacity-90 mb-8">
                Join our AI-powered CTF platform and learn cybersecurity skills through hands-on challenges
                that adapt to your learning pace.
              </p>

              {/* Floating code snippet */}
              <motion.div
                className="bg-black bg-opacity-30 backdrop-blur-sm rounded-lg p-6 font-mono text-left text-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
              >
                <div className="text-green-400">
                  <span className="text-gray-400">$</span> python exploit.py
                </div>
                <div className="text-white mt-2">
                  [+] Analyzing target...<br />
                  [+] Vulnerability found: SQL Injection<br />
                  [+] Crafting payload...<br />
                  <span className="text-yellow-400">[SUCCESS]</span> Flag captured: flag&#123;h4ck3r_m0d3&#125;
                </div>
              </motion.div>

              {/* Floating elements */}
              <div className="absolute top-10 left-10 w-16 h-16 bg-white bg-opacity-10 rounded-lg backdrop-blur-sm flex items-center justify-center">
                <span className="text-2xl">🔐</span>
              </div>
              <div className="absolute top-20 right-16 w-12 h-12 bg-white bg-opacity-10 rounded-lg backdrop-blur-sm flex items-center justify-center">
                <span className="text-xl">🛡️</span>
              </div>
              <div className="absolute bottom-20 left-20 w-14 h-14 bg-white bg-opacity-10 rounded-lg backdrop-blur-sm flex items-center justify-center">
                <span className="text-xl">🔍</span>
              </div>
              <div className="absolute bottom-32 right-12 w-10 h-10 bg-white bg-opacity-10 rounded-lg backdrop-blur-sm flex items-center justify-center">
                <span className="text-lg">💻</span>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;