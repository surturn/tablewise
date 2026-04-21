import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface OrderItem {
  id: string;
  menu_item_id: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  special_instructions?: string;
}

export interface Order {
  id: string;
  branch_id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  is_delivery: boolean;
  delivery_address?: string;
  notes?: string;
  items: OrderItem[];
  created_at?: string;
}

// Fetch all orders
export const useOrders = () => {
  return useQuery({
    queryKey: ['orders'],
    queryFn: async (): Promise<Order[]> => {
      const { data } = await apiClient.get('/orders/');
      return data;
    },
    refetchInterval: 5000, // Poll every 5 seconds for real-time feel
  });
};

// Update order status mutation
export const useUpdateOrderStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ orderId, status }: { orderId: string; status: string }) => {
      const { data } = await apiClient.patch(`/orders/${orderId}/status`, { status });
      return data;
    },
    onSuccess: () => {
      // Invalidate and refetch orders immediately after a successful update
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
};