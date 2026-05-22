import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { isStaffRole, ROLE_DASHBOARD_MAP } from '../constants/roles';

export const useAuthRedirect = () => {
  const { role } = useAuth();
  const navigate = useNavigate();

  const redirectBasedOnRole = (fromPath?: string, overrideRole?: string) => {
    const effectiveRole = overrideRole || role;
    if (!effectiveRole) {
      navigate('/login');
      return;
    }

    if (effectiveRole === 'customer') {
      navigate(fromPath || '/customer/dashboard');
    } else if (isStaffRole(effectiveRole)) {
      const targetPath = ROLE_DASHBOARD_MAP[effectiveRole] || '/dashboard';
      navigate(targetPath);
    } else {
      // Fallback
      navigate('/');
    }
  };

  return { redirectBasedOnRole };
};
