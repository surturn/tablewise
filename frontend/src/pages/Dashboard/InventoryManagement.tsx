import React, { useState } from 'react';
import { AlertTriangle, Plus, Minus, Package } from 'lucide-react';
import { useInventory, useAdjustStock, InventoryItem } from '../../api/inventory';

const InventoryManagement: React.FC = () => {
  const { data: inventory, isLoading, error } = useInventory();
  const adjustStock = useAdjustStock();

  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [adjustmentValue, setAdjustmentValue] = useState<number | ''>('');
  const [adjustmentType, setAdjustmentType] = useState<'add' | 'subtract'>('add');

  if (isLoading) return <div className="text-gray-500">Loading inventory data...</div>;
  if (error) return <div className="text-red-500">Failed to load inventory.</div>;

  const handleAdjustSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem || adjustmentValue === '') return;

    const val = Number(adjustmentValue);
    const quantity_added = adjustmentType === 'add' ? val : -val;

    adjustStock.mutate({ id: selectedItem.id, quantity_added }, {
      onSuccess: () => {
        setSelectedItem(null);
        setAdjustmentValue('');
      }
    });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Package className="text-brand-orange" /> Stock Management
        </h2>
        {/* Future feature: Filter by branch for Owners */}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex-1">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Stock</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {inventory?.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                  No inventory items found. Run the seed script to populate.
                </td>
              </tr>
            ) : (
              inventory?.map((item) => {
                const isLowStock = item.quantity <= item.low_stock_threshold;
                return (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                      {item.sku && <div className="text-xs text-gray-500">SKU: {item.sku}</div>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-gray-800">
                        {Number(item.quantity).toFixed(2)} {item.unit}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {isLowStock ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <AlertTriangle size={12} /> Low Stock
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Healthy
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => setSelectedItem(item)}
                        className="text-brand-orange hover:text-orange-700 font-bold"
                      >
                        Adjust Stock
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Adjust Stock Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-1">Adjust {selectedItem.name}</h3>
            <p className="text-sm text-gray-500 mb-6">Current Stock: {Number(selectedItem.quantity).toFixed(2)} {selectedItem.unit}</p>

            <form onSubmit={handleAdjustSubmit} className="space-y-4">
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setAdjustmentType('add')}
                  className={`flex-1 flex justify-center items-center gap-2 py-3 border rounded-lg font-medium transition-colors ${
                    adjustmentType === 'add' ? 'bg-green-50 border-green-500 text-green-700' : 'bg-white text-gray-500'
                  }`}
                >
                  <Plus size={18} /> Add Stock
                </button>
                <button
                  type="button"
                  onClick={() => setAdjustmentType('subtract')}
                  className={`flex-1 flex justify-center items-center gap-2 py-3 border rounded-lg font-medium transition-colors ${
                    adjustmentType === 'subtract' ? 'bg-red-50 border-red-500 text-red-700' : 'bg-white text-gray-500'
                  }`}
                >
                  <Minus size={18} /> Subtract (Waste)
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity ({selectedItem.unit})</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={adjustmentValue}
                  onChange={(e) => setAdjustmentValue(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-orange focus:border-brand-orange outline-none"
                  placeholder={`Enter amount to ${adjustmentType}`}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setSelectedItem(null)}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={adjustStock.isPending}
                  className="flex-1 px-4 py-3 bg-brand-dark text-white rounded-lg hover:bg-black font-medium transition-colors disabled:opacity-50"
                >
                  {adjustStock.isPending ? 'Saving...' : 'Confirm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryManagement;