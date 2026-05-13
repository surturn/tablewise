import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { useOrdersWebSocket } from '../hooks/useOrdersWebSocket';

export interface OrderItem {
  id: string;
  menu_item_id: string;
  quantity: number;
  unit_price_usd_cents: number;
  subtotal_usd_cents: number;
  special_instructions?: string;
}

export interface Order {
  id: string;
  outlet_id: string;
  guest_id: string;
  status: string;
  total_usd_cents: number;
  order_type: 'dine_in' | 'delivery' | 'takeaway' | 'room_service';
  table_number?: string;
  room_id?: string;
  is_delivery: boolean;
  delivery_address?: string;
  notes?: string;
  items: OrderItem[];
  updated_at?: string;
  created_at?: string;
}

export interface PaginatedOrders {
  items: Order[];
  total: number;
  page: number;
  pages: number;
}

export const useOrders = (outletId?: string) => {
  useOrdersWebSocket(outletId);
  return useQuery({
    queryKey: ['orders', outletId],
    queryFn: async (): Promise<PaginatedOrders> => {
      const { data } = await apiClient.get('/orders/', { params: { outlet_id: outletId } });
      return data;
    },
      });
};

export const useUpdateOrderStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ orderId, status }: { orderId: string; status: string }) => {
      const { data } = await apiClient.patch(`/orders/${orderId}/status`, { status });
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
  });
};
