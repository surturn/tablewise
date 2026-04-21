import React from 'react';
// Added OrderItem to the import to fix the 'item' implicitly any error
import { useOrders, useUpdateOrderStatus, Order, OrderItem } from '@/api/orders.ts';
// Removed 'Truck' to fix TS6133
import { CheckCircle, ChefHat, PackageCheck } from 'lucide-react';

const OrdersFeed: React.FC = () => {
  const { data: orders, isLoading, error } = useOrders();
  const updateStatus = useUpdateOrderStatus();

  if (isLoading) return <div className="text-gray-500">Loading live orders...</div>;
  if (error) return <div className="text-red-500">Failed to load orders.</div>;

  // FIX: Explicitly typed 'o' as 'Order'
  const activeOrders = orders?.filter((o: Order) =>
    !['delivered', 'cancelled', 'payment_failed', 'expired', 'created', 'pending_payment'].includes(o.status)
  ) || [];

  const columns = [
    { title: 'New (Paid)', status: 'paid', icon: CheckCircle, color: 'bg-blue-50 border-blue-200 text-blue-700', nextAction: 'confirmed', btnText: 'Acknowledge' },
    { title: 'Confirmed', status: 'confirmed', icon: ChefHat, color: 'bg-yellow-50 border-yellow-200 text-yellow-700', nextAction: 'preparing', btnText: 'Send to Kitchen' },
    { title: 'Preparing', status: 'preparing', icon: ChefHat, color: 'bg-orange-50 border-orange-200 text-orange-700', nextAction: 'ready', btnText: 'Mark Ready' },
    { title: 'Ready', status: 'ready', icon: PackageCheck, color: 'bg-green-50 border-green-200 text-green-700', nextAction: 'dispatched', btnText: 'Dispatch' },
  ];

  const handleStatusChange = (orderId: string, nextStatus: string) => {
    updateStatus.mutate({ orderId, status: nextStatus });
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Kitchen Display System</h2>
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm font-medium text-gray-600">Live Sync Active</span>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 overflow-x-auto pb-4">
        {columns.map((col) => {
          // FIX: Explicitly typed 'o' as 'Order'
          const colOrders = activeOrders.filter((o: Order) => o.status === col.status);
          const Icon = col.icon;

          return (
            <div key={col.status} className="flex flex-col bg-gray-100/50 rounded-xl p-4 border border-gray-200 min-w-[300px]">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border mb-4 ${col.color}`}>
                <Icon size={20} />
                <h3 className="font-bold">{col.title} ({colOrders.length})</h3>
              </div>

              <div className="flex-1 overflow-y-auto space-y-4 pr-1">
                {colOrders.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-8">No orders</p>
                ) : (
                  colOrders.map((order: Order) => (
                    <div key={order.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex flex-col">
                      <div className="flex justify-between items-start mb-3 border-b pb-2">
                        <div>
                          <span className="text-xs font-bold text-gray-400">#{order.id.slice(0, 8)}</span>
                          <div className="font-bold text-gray-800 mt-1">
                            {order.is_delivery ? <span className="text-brand-orange">Delivery</span> : <span>Pickup</span>}
                          </div>
                        </div>
                        <span className="text-sm font-bold bg-gray-100 px-2 py-1 rounded">
                          KES {order.total_amount}
                        </span>
                      </div>

                      <div className="flex-1 mb-4">
                        <ul className="space-y-2 text-sm">
                          {/* FIX: Explicitly typed 'item' as 'OrderItem' (or you could use 'any' if you don't have the type yet) */}
                          {order.items.map((item: OrderItem) => (
                            <li key={item.id} className="flex justify-between font-medium text-gray-700">
                              <span>{item.quantity}x Item</span>
                              <span className="text-gray-400">KES {item.subtotal}</span>
                            </li>
                          ))}
                        </ul>
                        {order.notes && (
                          <div className="mt-3 p-2 bg-yellow-50 border border-yellow-100 rounded text-xs text-yellow-800 font-medium">
                            Note: {order.notes}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => handleStatusChange(order.id, col.nextAction)}
                        disabled={updateStatus.isPending}
                        className="mt-auto w-full py-2 bg-brand-dark text-white rounded font-medium hover:bg-black transition-colors disabled:opacity-50"
                      >
                        {col.btnText}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OrdersFeed;