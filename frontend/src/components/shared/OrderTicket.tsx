import { cn } from './ProductCard';
import { StatusBadge } from './StatusBadge';
import { Trash2 } from 'lucide-react';

interface TicketItem {
  id: string;
  name: string;
  quantity: number;
  price_usd_cents: number;
  voided?: boolean;
}

interface OrderTicketProps {
  orderId: string;
  tableOrRoom?: string;
  waiterId?: string;
  status: 'pending' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  items: TicketItem[];
  type: 'dine_in' | 'takeaway' | 'room_service';
  onUpdateStatus?: (status: string) => void;
  onVoidItem?: (itemId: string) => void;
  className?: string;
}

export function OrderTicket({
  orderId,
  tableOrRoom,
  waiterId,
  status,
  items,
  type,
  onUpdateStatus,
  onVoidItem,
  className
}: OrderTicketProps) {
  const subtotal = items.reduce((acc, item) => item.voided ? acc : acc + (item.price_usd_cents * item.quantity), 0);

  return (
    <div className={cn("bg-white border border-neutral-200 rounded-lg shadow-sm flex flex-col", className)}>
      {/* Header */}
      <div className="p-4 border-b border-neutral-100 flex items-start justify-between bg-neutral-50 rounded-t-lg">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-lg text-neutral-900">#{orderId.slice(-6).toUpperCase()}</h3>
            <StatusBadge status={status} />
          </div>
          <div className="text-sm text-neutral-500 font-medium flex gap-3">
            {type === 'dine_in' && <span>Table {tableOrRoom}</span>}
            {type === 'room_service' && <span>Room {tableOrRoom}</span>}
            {type === 'takeaway' && <span>Takeaway</span>}
            {waiterId && <span>• Waiter {waiterId.slice(0, 4)}</span>}
          </div>
        </div>
      </div>

      {/* Items */}
      <div className="p-4 flex-1 overflow-y-auto">
        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id} className={cn("flex justify-between items-start", item.voided && "opacity-50 line-through")}>
              <div className="flex gap-2 items-start">
                <span className="font-medium text-neutral-700">{item.quantity}x</span>
                <div>
                  <p className="text-neutral-900 font-medium">{item.name}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-neutral-600">${((item.price_usd_cents * item.quantity) / 100).toFixed(2)}</span>
                {onVoidItem && !item.voided && status === 'pending' && (
                  <button onClick={() => onVoidItem(item.id)} className="text-red-500 hover:text-red-700">
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-100 bg-neutral-50 rounded-b-lg">
        <div className="flex justify-between items-center mb-4">
          <span className="font-semibold text-neutral-700">Total</span>
          <span className="font-bold text-xl text-neutral-900">${(subtotal / 100).toFixed(2)}</span>
        </div>
        {onUpdateStatus && status === 'pending' && (
          <button 
            onClick={() => onUpdateStatus('preparing')}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
          >
            Mark as Preparing
          </button>
        )}
        {onUpdateStatus && status === 'preparing' && (
          <button 
            onClick={() => onUpdateStatus('ready')}
            className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors"
          >
            Mark as Ready
          </button>
        )}
      </div>
    </div>
  );
}
