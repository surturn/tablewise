import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { PaginatedOrders, Order } from '../api/orders';

export function useOrdersWebSocket(outletId?: string) {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);

  useEffect(() => {
    if (!outletId) return;

    let isMounted = true;
    let baseUrl = import.meta.env.VITE_API_BASE_URL;
    
    if (!baseUrl) {
      if (import.meta.env.PROD) {
        console.error('VITE_API_BASE_URL is missing in production environment variables.');
        return;
      } else {
        baseUrl = 'http://localhost:8000';
      }
    }

    const connect = () => {
      if (!isMounted) return;

      // Extract JWT securely (handles plain token storage or Zustand persisted state)
      let token = '';
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        try {
          const parsed = JSON.parse(authStorage);
          token = parsed.state?.token || parsed.token || '';
        } catch (e) {
          token = localStorage.getItem('token') || '';
        }
      } else {
        token = localStorage.getItem('token') || '';
      }

      if (!token) {
        console.error("WebSocket blocked: Auth token missing");
        return;
      }

      // Attach token as a query parameter
      const wsUrl = new URL(baseUrl.replace(/^http/, 'ws') + `/ws/orders/${outletId}`);
      wsUrl.searchParams.append('token', token);

      const socket = new WebSocket(wsUrl.toString());
      wsRef.current = socket;

      socket.onopen = () => {
        reconnectAttemptsRef.current = 0; // Reset backoff on success
        console.log('Orders WebSocket connected securely');
      };

      socket.onmessage = (event) => {
        const update = JSON.parse(event.data) as { type: string; order_id: string; status: string; updated_at: string };
        if (update.type !== 'order_update') return;
        
        queryClient.setQueryData<PaginatedOrders>(['orders', outletId], (current) => {
          if (!current) return current;
          return {
            ...current,
            items: current.items.map((order: Order) =>
              order.id === update.order_id 
                ? { ...order, status: update.status, updated_at: update.updated_at } 
                : order
            ),
          };
        });
      };

      socket.onclose = (event) => {
        wsRef.current = null;
        if (!isMounted) return;

        // 4001 indicates a strict Auth/Role violation. Do NOT infinitely retry.
        if (event.code === 4001) {
          console.error(`WebSocket closed by server (Auth Error): ${event.reason}`);
          return;
        }

        // Exponential backoff logic (1s -> 30s max)
        const attempts = reconnectAttemptsRef.current;
        const baseDelay = Math.min(1000 * Math.pow(2, attempts), 30000);
        
        // Add random jitter (±20%) to prevent thundering herd
        const jitter = baseDelay * 0.2 * (Math.random() * 2 - 1);
        const delay = Math.floor(baseDelay + jitter);

        reconnectAttemptsRef.current += 1;
        
        console.log(`WebSocket disconnected. Reconnecting in ${delay}ms...`);
        reconnectTimeoutRef.current = window.setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [outletId, queryClient]);
}
