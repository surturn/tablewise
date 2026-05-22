import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuthStore, User as StoreUser } from '../store/authStore';
import { UserRole, isStaffRole } from '../constants/roles';

// Simple base64 decoding for JWT payload (no external deps)
const decodeJwtRole = (token: string): string | null => {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const payload = JSON.parse(jsonPayload);
    return payload.role || null;
  } catch (e) {
    console.error("Failed to decode JWT role", e);
    return null;
  }
};

const checkTokenExpiry = (token: string): boolean => {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return true;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    if (!payload.exp) return false;
    // Return true if expired (current time > expiry time)
    return Date.now() >= payload.exp * 1000;
  } catch (e) {
    return true; // if we can't parse it, consider it expired
  }
};

interface AuthContextType {
  user: StoreUser | null;
  token: string | null;
  isAuthenticated: boolean;
  role: UserRole | null;
  isCustomer: () => boolean;
  isStaff: () => boolean;
  hasRole: (allowedRoles: UserRole[]) => boolean;
  login: (token: string, user: StoreUser) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const storeToken = useAuthStore((state) => state.token);
  const storeUser = useAuthStore((state) => state.user);
  const storeSetAuth = useAuthStore((state) => state.setAuth);
  const storeLogout = useAuthStore((state) => state.logout);

  const [role, setRole] = useState<UserRole | null>(null);

  useEffect(() => {
    if (storeToken) {
      if (checkTokenExpiry(storeToken)) {
        storeLogout();
        setRole(null);
      } else {
        const decodedRole = decodeJwtRole(storeToken);
        setRole(decodedRole as UserRole);
      }
    } else {
      setRole(null);
    }
  }, [storeToken, storeLogout]);

  // Set up polling for token expiry
  useEffect(() => {
    if (!storeToken) return;

    const interval = setInterval(() => {
      if (checkTokenExpiry(storeToken)) {
        storeLogout();
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [storeToken, storeLogout]);


  const isAuthenticated = !!storeToken && !checkTokenExpiry(storeToken);

  const value: AuthContextType = {
    user: storeUser,
    token: isAuthenticated ? storeToken : null,
    isAuthenticated,
    role,
    isCustomer: () => role === 'customer',
    isStaff: () => role !== null && isStaffRole(role),
    hasRole: (allowedRoles) => role !== null && allowedRoles.includes(role),
    login: (token, user) => {
      storeSetAuth(token, user);
      setRole(decodeJwtRole(token) as UserRole);
    },
    logout: () => {
      storeLogout();
      setRole(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
