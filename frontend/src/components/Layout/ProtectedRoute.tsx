import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { UserRole, isStaffRole, ROLE_DASHBOARD_MAP } from '../../constants/roles';

interface ProtectedRouteProps {
  children?: React.ReactNode;
  roles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, roles }) => {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (roles && role && !roles.includes(role)) {
    // Authenticated but wrong role
    if (role === 'customer') {
      return <Navigate to="/" replace />;
    } else if (isStaffRole(role)) {
      const targetPath = ROLE_DASHBOARD_MAP[role] || '/dashboard';
      return <Navigate to={targetPath} replace />;
    }
    return <Navigate to="/" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};