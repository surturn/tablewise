import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore.ts';

export const ProtectedRoute: React.FC = () => {
  const token = useAuthStore((state) => state.token);

  // If no token exists, bump them to the login page
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Otherwise, render the child routes (Outlet)
  return <Outlet />;
};