import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { PaginatedOrders, Order } from '../api/orders';

export function useOrdersWebSocket(outletId?: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!outletId) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/orders/${outletId}`);

    socket.onmessage = (event) => {
      const update = JSON.parse(event.data) as { type: string; order_id: string; status: string; updated_at: string };
      if (update.type !== 'order_update') return;
      queryClient.setQueryData<PaginatedOrders>(['orders', outletId], (current) => {
        if (!current) return current;
        return {
          ...current,
          items: current.items.map((order: Order) =>
            order.id === update.order_id ? { ...order, status: update.status, updated_at: update.updated_at } : order,
          ),
        };
      });
    };

    return () => socket.close();
  }, [outletId, queryClient]);
}
