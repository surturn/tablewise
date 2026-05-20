import React, { useState } from 'react';
import { useInventory, useAdjustStock } from '../../api/inventory';
import { fetchOutlets } from '../../api/outlets';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../../store/authStore';
import { SkeletonTable } from '../../components/ui/Skeleton';
import { Package, Search, Plus, Minus } from 'lucide-react';
import { m } from 'framer-motion';

const InventoryManagement: React.FC = () => {
  const { user } = useAuthStore();
  const [search, setSearch] = useState('');
  
  const { data: outlets } = useQuery({ queryKey: ['outlets'], queryFn: fetchOutlets });
  const [selectedOutlet, setSelectedOutlet] = useState<string | undefined>(user?.outlet_id);

  const { data: inventory, isLoading } = useInventory(selectedOutlet);
  const adjustStock = useAdjustStock();

  const handleAdjust = (id: string, quantity_added: number) => {
    adjustStock.mutate({ id, quantity_added });
  };

  const filteredInventory = inventory?.filter((item) =>
    item.name.toLowerCase().includes(search.toLowerCase()) ||
    item.sku?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-brand-dark flex items-center gap-2">
          <Package className="text-brand-orange" /> Inventory Management
        </h2>
        
        <div className="flex items-center gap-4 w-full sm:w-auto">
          {!user?.outlet_id && (
            <select
              value={selectedOutlet || ''}
              onChange={(e) => setSelectedOutlet(e.target.value || undefined)}
              className="border border-stone-200 rounded-lg p-2 outline-none focus:ring-2 focus:ring-brand-orange bg-white"
            >
              <option value="">All Outlets</option>
              {outlets?.map(o => (
                <option key={o.id} value={o.id}>{o.name}</option>
              ))}
            </select>
          )}
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={18} />
            <input
              type="text"
              placeholder="Search items or SKU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange transition-all"
            />
          </div>
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
                  <th className="px-6 py-4 font-bold text-brand-dark">Item Name</th>
                  <th className="px-6 py-4 font-bold text-brand-dark">SKU</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-right">In Stock</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-center">Unit</th>
                  <th className="px-6 py-4 font-bold text-brand-dark">Status</th>
                  <th className="px-6 py-4 font-bold text-brand-dark text-right">Adjust</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {filteredInventory?.map((item) => {
                  const isLowStock = item.quantity <= item.low_stock_threshold;
                  return (
                    <tr key={item.id} className="hover:bg-stone-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-brand-dark">{item.name}</td>
                      <td className="px-6 py-4 text-stone-400">{item.sku || '-'}</td>
                      <td className="px-6 py-4 text-right font-bold text-brand-dark">{item.quantity}</td>
                      <td className="px-6 py-4 text-center">{item.unit}</td>
                      <td className="px-6 py-4">
                        {isLowStock ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">Low Stock</span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">Optimal</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleAdjust(item.id, -1)}
                            disabled={adjustStock.isPending}
                            className="p-1.5 rounded-md hover:bg-stone-200 text-stone-500 transition-colors"
                          >
                            <Minus size={16} />
                          </button>
                          <button
                            onClick={() => handleAdjust(item.id, 1)}
                            disabled={adjustStock.isPending}
                            className="p-1.5 rounded-md hover:bg-stone-200 text-stone-500 transition-colors"
                          >
                            <Plus size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {filteredInventory?.length === 0 && (
              <div className="p-12 text-center text-stone-500">
                No inventory items found.
              </div>
            )}
          </div>
        )}
      </m.div>
    </div>
  );
};

export default InventoryManagement;