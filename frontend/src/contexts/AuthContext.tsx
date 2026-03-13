import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, LoginForm, RegisterForm } from '../types';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  token: string | null;
  login: (data: LoginForm) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => Promise<void>;
  updateUserProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if we have a stored token and validate it
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('access_token');

      if (storedToken) {
        try {
          // Verify token with backend
          const response = await authService.verifyToken(storedToken);
          if (response.valid) {
            // Get user info
            const userInfo = await authService.getCurrentUser(storedToken);
            setUser(userInfo);
            setToken(storedToken);
          } else {
            // Token invalid, clear it
            localStorage.removeItem('access_token');
            setToken(null);
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }

      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (data: LoginForm): Promise<void> => {
    try {
      setLoading(true);

      const response = await authService.login(data.email, data.password);

      // Store token
      localStorage.setItem('access_token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);

      toast.success('Welcome back!');
    } catch (error: any) {
      console.error('Login error:', error);
      let message = 'Login failed';

      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }

      toast.error(message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterForm): Promise<void> => {
    try {
      setLoading(true);

      const response = await authService.register({
        email: data.email,
        username: data.username,
        password: data.password,
        display_name: data.display_name,
        skill_level: data.skill_level || 'beginner'
      });

      // Store token
      localStorage.setItem('access_token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);

      toast.success('Account created successfully!');
    } catch (error: any) {
      console.error('Registration error:', error);
      let message = 'Registration failed';

      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }

      toast.error(message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Clear token and user
      localStorage.removeItem('access_token');
      setToken(null);
      setUser(null);

      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed');
      throw error;
    }
  };

  const updateUserProfile = async (data: Partial<User>): Promise<void> => {
    if (!user || !token) throw new Error('No user logged in');

    try {
      const response = await authService.updateProfile(data, token);
      setUser(response);
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error('Failed to update profile');
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    token,
    login,
    register,
    logout,
    updateUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
