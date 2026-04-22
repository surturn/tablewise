import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Store, MapPin, Phone, Clock, Loader2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchBranches } from '../../api/branches';

const DashboardHome: React.FC = () => {
  const { data: branches =[], isLoading, isError } = useQuery({
    queryKey: ['branches'],
    queryFn: fetchBranches,
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#121212]">Dashboard Overview</h1>
        <p className="text-sm text-gray-500">Welcome back. Here is the status of your restaurant branches.</p>
      </div>

      {/* Quick Actions (Optional but helpful for navigation) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link to="/dashboard/orders" className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center justify-between hover:border-[#FF6B00] transition-colors">
          <span className="font-medium text-[#121212]">View Live Orders</span>
          <ArrowRight size={18} className="text-[#FF6B00]" />
        </Link>
        <Link to="/dashboard/inventory" className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center justify-between hover:border-[#FF6B00] transition-colors">
          <span className="font-medium text-[#121212]">Manage Inventory</span>
          <ArrowRight size={18} className="text-[#FF6B00]" />
        </Link>
        <Link to="/dashboard/analytics" className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center justify-between hover:border-[#FF6B00] transition-colors">
          <span className="font-medium text-[#121212]">AI Forecasting</span>
          <ArrowRight size={18} className="text-[#FF6B00]" />
        </Link>
      </div>

      {/* Branches Section */}
      <div className="flex items-center justify-between mt-8 mb-4">
        <h2 className="text-xl font-bold text-[#121212] flex items-center gap-2">
          <Store className="text-[#FF6B00]" /> Active Branches
        </h2>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-[#FF6B00]" size={40} />
        </div>
      ) : isError ? (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100">
          Failed to load branches. Please ensure the backend is running.
        </div>
      ) : branches.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-100 text-center">
          <Store size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No branches found. Please add a branch via the backend or database.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((branch) => (
            <div key={branch.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
              {/* Card Header */}
              <div className="p-5 border-b border-gray-50 flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-[#121212]">{branch.name}</h3>
                  <div className="flex items-center gap-1 text-sm text-gray-500 mt-1">
                    <MapPin size={14} />
                    <span>{branch.location}</span>
                  </div>
                </div>
                {branch.is_active ? (
                  <span className="px-2.5 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">Open</span>
                ) : (
                  <span className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-bold rounded-full">Closed</span>
                )}
              </div>

              {/* Card Body */}
              <div className="p-5 space-y-3 bg-gray-50/50">
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <Phone size={16} className="text-gray-400" />
                  <span>{branch.contact_number}</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <Clock size={16} className="text-gray-400" />
                  <span>{branch.opening_time} - {branch.closing_time}</span>
                </div>
              </div>

              {/* Card Footer */}
              <div className="p-4 bg-white border-t border-gray-100">
                <button className="w-full text-center text-sm font-medium text-[#FF6B00] hover:text-[#e66000] transition-colors">
                  View Branch Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardHome;