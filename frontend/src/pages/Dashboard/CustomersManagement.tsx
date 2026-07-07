import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchGuests } from '../../api/guests';
import { SkeletonTable } from '../../components/ui/Skeleton';
import { Users, Search, Award } from 'lucide-react';
import { m } from 'framer-motion';

const CustomersManagement: React.FC = () => {
  const { data: guests, isLoading } = useQuery({ queryKey: ['guests'], queryFn: fetchGuests });
  const [search, setSearch] = useState('');

  const filteredGuests = guests?.filter(
    (g) => g.full_name.toLowerCase().includes(search.toLowerCase()) || g.phone_number.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-brand-dark flex items-center gap-2">
          <Users className="text-brand-orange" /> Guest Directory
        </h2>
        
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={18} />
          <input
            type="text"
            placeholder="Search guests..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange transition-all bg-white"
          />
        </div>
      </div>

      <m.div className="bg-white rounded-2xl shadow-subtle border border-stone-200 overflow-hidden">
        {isLoading ? (
          <SkeletonTable rows={8} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-stone-600">
              <thead className="bg-stone-50 border-b border-stone-200">
                <tr>
                  <th className="px-6 py-4 font-bold text-brand-dark">Full Name</th>
                  <th className="px-6 py-4 font-bold text-brand-dark">Contact</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-center">Nationality</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-right">Total Spend</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-right">Loyalty Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {filteredGuests?.map((guest) => (
                  <tr key={guest.id} className="hover:bg-stone-50 transition-colors">
                    <td className="px-6 py-4 font-bold text-brand-dark">{guest.full_name}</td>
                    <td className="px-6 py-4">
                      <div>{guest.phone_number}</div>
                      <div className="text-xs text-stone-400">{guest.email}</div>
                    </td>
                    <td className="px-6 py-4 text-center">{guest.nationality || '-'}</td>
                    <td className="px-6 py-4 text-right font-medium">KSh {(guest.total_spend_kes_cents / 100).toFixed(2)}</td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-2 py-1 rounded-full font-bold border border-amber-200">
                        <Award size={14} /> {guest.loyalty_points}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredGuests?.length === 0 && (
              <div className="p-12 text-center text-stone-500">
                No guests found.
              </div>
            )}
          </div>
        )}
      </m.div>
    </div>
  );
};

export default CustomersManagement;