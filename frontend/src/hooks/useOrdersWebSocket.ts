import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { PaginatedOrders, Order } from '../api/orders';

export function useOrdersWebSocket(outletId?: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!outletId) return;
    let baseUrl = import.meta.env.VITE_API_BASE_URL;
    if (!baseUrl) {
      if (import.meta.env.PROD) {
        console.error('VITE_API_BASE_URL is missing in production environment variables.');
        return;
      } else {
        baseUrl = 'http://localhost:8000';
      }
    }
    const wsUrl = baseUrl.replace(/^http/, 'ws') + `/ws/orders/${outletId}`;
    const socket = new WebSocket(wsUrl);

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
