import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Search, Award } from 'lucide-react';
import { fetchCustomers } from '@/api/customers.ts';

const CustomersManagement: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: customers =[], isLoading, isError } = useQuery({
    queryKey: ['customers'],
    queryFn: fetchCustomers,
  });

  const filteredCustomers = customers.filter(c =>
    c.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.phone_number.includes(searchTerm)
  );

  if (isLoading) return <div className="p-6 text-gray-500">Loading customers...</div>;
  if (isError) return <div className="p-6 text-red-500">Failed to load customers.</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#121212] flex items-center gap-2">
            <Users className="text-[#FF6B00]" /> Customers Directory
          </h1>
          <p className="text-sm text-gray-500">Manage your restaurant's customer base and loyalty points.</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-gray-100 flex items-center">
          <div className="relative w-full max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by name or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-[#FF6B00]"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-600 text-sm border-b border-gray-200">
                <th className="px-6 py-3 font-medium">Name</th>
                <th className="px-6 py-3 font-medium">Phone Number</th>
                <th className="px-6 py-3 font-medium">Email</th>
                <th className="px-6 py-3 font-medium text-right">Loyalty Points</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredCustomers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    No customers found.
                  </td>
                </tr>
              ) : (
                filteredCustomers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-[#121212]">{customer.full_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{customer.phone_number}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{customer.email || '-'}</td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 font-semibold text-[#FF6B00]">
                        <Award size={16} /> {customer.loyalty_points}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CustomersManagement;