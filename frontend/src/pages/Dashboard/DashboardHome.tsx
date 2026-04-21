import React from 'react';
import { useAuthStore } from '@/store/authStore.ts';

const DashboardHome: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <div>
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome back, {user?.full_name}!</h2>
        <p className="text-gray-600">
          You are logged in as a <strong className="capitalize text-brand-orange">{user?.role.replace('_', ' ')}</strong>.
          {user?.branch_id ? ' Your dashboard is filtered to your branch.' : ' You have global access across all branches.'}
        </p>
      </div>
    </div>
  );
};

export default DashboardHome;