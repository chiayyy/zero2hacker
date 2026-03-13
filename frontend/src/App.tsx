import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { useTheme } from './contexts/ThemeContext';

// Layout Components
import Layout from './components/layout/Layout';
import AuthLayout from './components/layout/AuthLayout';

// Page Components
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Challenges from './pages/Challenges';
import ChallengeDetail from './pages/ChallengeDetail';
import Leaderboard from './pages/Leaderboard';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import AdminPanel from './pages/AdminPanel';
import Lab from './pages/Lab';
import GenerateChallengePage from './pages/GenerateChallengePage';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// Loading Component
import LoadingSpinner from './components/ui/LoadingSpinner';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
  children,
  adminOnly = false
}) => {
  const { user, loading } = useAuth();

  console.log('ProtectedRoute - loading:', loading, 'user:', user);

  if (loading) {
    console.log('ProtectedRoute: Still loading...');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    console.log('ProtectedRoute: No user, redirecting to login');
    return <Navigate to="/auth/login" replace />;
  }

  if (adminOnly && user.role !== 'admin') {
    console.log('ProtectedRoute: Not admin, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }

  console.log('ProtectedRoute: Access granted');
  return <>{children}</>;
};

// Public Route Component (redirect if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { darkMode } = useTheme();

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gray-50 dark:bg-dark-900 transition-colors duration-200">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />

          {/* Auth Routes */}
          <Route path="/auth/*" element={
            <PublicRoute>
              <AuthLayout>
                <Routes>
                  <Route path="login" element={<Login />} />
                  <Route path="register" element={<Register />} />
                </Routes>
              </AuthLayout>
            </PublicRoute>
          } />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/challenges" element={
            <ProtectedRoute>
              <Layout>
                <Challenges />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/challenges/:id" element={
            <ProtectedRoute>
              <Layout>
                <ChallengeDetail />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/leaderboard" element={
            <ProtectedRoute>
              <Layout>
                <Leaderboard />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/analytics" element={
            <ProtectedRoute>
              <Layout>
                <Analytics />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/generate-challenge" element={
            <ProtectedRoute>
              <Layout>
                <GenerateChallengePage />
              </Layout>
            </ProtectedRoute>
          } />

          {/* Lab Routes */}
          <Route path="/lab" element={
            <ProtectedRoute>
              <Layout>
                <Lab />
              </Layout>
            </ProtectedRoute>
          } />

          <Route path="/lab/:labId" element={
            <ProtectedRoute>
              <Layout>
                <Lab />
              </Layout>
            </ProtectedRoute>
          } />

          {/* Admin Routes */}
          <Route path="/admin/*" element={
            <ProtectedRoute adminOnly>
              <Layout>
                <AdminPanel />
              </Layout>
            </ProtectedRoute>
          } />

          {/* Catch all - redirect to dashboard if authenticated, home if not */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;