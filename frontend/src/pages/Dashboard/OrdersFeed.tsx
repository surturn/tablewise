import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { m, AnimatePresence } from 'framer-motion';
import { useOrdersWebSocket } from '../../hooks/useOrdersWebSocket';
import { useUpdateOrderStatus } from '../../api/orders';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../store/authStore';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { EmptyState } from '../../components/ui/EmptyState';
import { ShoppingBag, CheckCircle } from 'lucide-react';
import { useToastStore } from '../../store/toastStore';

const OrdersFeed: React.FC = () => {
  const { user } = useAuthStore();
  const [filter, setFilter] = useState('active');
  const addToast = useToastStore(s => s.addToast);

  const { data: initialOrders, isLoading } = useQuery({
    queryKey: ['orders', user?.outlet_id, filter],
    queryFn: async () => {
      const { data } = await apiClient.get('/orders/', {
        params: { outlet_id: user?.outlet_id, limit: 50 },
      });
      return data.items || data;
    },
  });

  useOrdersWebSocket(user?.outlet_id || '');
  const updateStatus = useUpdateOrderStatus();

  const handleUpdateStatus = (orderId: string, newStatus: string) => {
    updateStatus.mutate({ orderId, status: newStatus }, {
      onSuccess: () => addToast('Order status updated', 'success'),
      onError: () => addToast('Failed to update status', 'error')
    });
  };

  const displayOrders = initialOrders || [];

  const filteredOrders = displayOrders.filter((order: any) => {
    if (filter === 'active') return !['completed', 'cancelled', 'delivered'].includes(order.status);
    if (filter === 'completed') return ['completed', 'delivered'].includes(order.status);
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-brand-dark flex items-center gap-2">
          <ShoppingBag className="text-brand-orange" /> POS & Orders Feed
        </h2>
        
        <div className="flex bg-stone-100 p-1 rounded-lg">
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${filter === 'active' ? 'bg-white text-brand-dark shadow-sm' : 'text-stone-500 hover:text-brand-dark'}`}
          >
            Active Orders
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${filter === 'completed' ? 'bg-white text-brand-dark shadow-sm' : 'text-stone-500 hover:text-brand-dark'}`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${filter === 'all' ? 'bg-white text-brand-dark shadow-sm' : 'text-stone-500 hover:text-brand-dark'}`}
          >
            All
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredOrders.map((order: any) => (
              <m.div
                key={order.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                layout
                className="bg-white p-5 rounded-2xl shadow-subtle border border-stone-200 flex flex-col"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="text-xs font-bold text-stone-400">#{order.id.slice(0, 8)}</span>
                    <h3 className="font-bold text-lg text-brand-dark mt-1">
                      {order.guest?.full_name || order.guest_id.slice(0, 8)}
                    </h3>
                  </div>
                  <StatusBadge status={order.status} />
                </div>

                <div className="flex-1 bg-stone-50 rounded-xl p-4 mb-4">
                  <ul className="space-y-2">
                    {order.items?.map((item: any) => (
                      <li key={item.id} className="flex justify-between text-sm">
                        <span className="font-medium text-brand-dark">{item.quantity}x {item.menu_item?.name || 'Item'}</span>
                        <span className="text-stone-500">KSh {((item.price_kes_cents * item.quantity) / 100).toFixed(2)}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex justify-between items-center pt-4 border-t border-stone-100">
                  <div>
                    <span className="text-xs text-stone-500 block mb-1">Total Amount</span>
                    <span className="font-black text-xl text-brand-dark">KSh {(order.total_kes_cents / 100).toFixed(2)}</span>
                  </div>
                  
                  <div className="flex gap-2">
                    {order.status === 'created' || order.status === 'pending_payment' ? (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'preparing')}
                        className="bg-brand-orange hover:bg-amber-400 text-white font-bold py-2 px-4 rounded-lg text-sm transition-colors"
                      >
                        Accept
                      </button>
                    ) : order.status === 'preparing' ? (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'ready')}
                        className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded-lg text-sm transition-colors"
                      >
                        Mark Ready
                      </button>
                    ) : order.status === 'ready' ? (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'completed')}
                        className="bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-4 rounded-lg text-sm transition-colors"
                      >
                        Complete
                      </button>
                    ) : null}
                  </div>
                </div>
              </m.div>
            ))}
          </AnimatePresence>
        </div>
      )}
      
      {!isLoading && filteredOrders.length === 0 && (
        <div className="py-12">
          <EmptyState 
            theme="light"
            icon={
              <m.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: [1.2, 1], opacity: 1 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
              >
                <CheckCircle size={40} className="text-green-500" />
              </m.div>
            }
            title={filter === 'completed' ? "No completed orders yet" : "Kitchen is all caught up!"}
            description={filter === 'completed' ? "Completed orders will appear here." : "Awaiting the next wave of service. Take a breather!"}
          />
        </div>
      )}
    </div>
  );
};

export default OrdersFeed;