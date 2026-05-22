import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface InventoryItem {
  id: string;
  name: string;
  sku: string | null;
  quantity: number;
  unit: string;
  low_stock_threshold: number;
  outlet_id: string;
}

// Fetch inventory (Backend handles RBAC scoping automatically based on JWT token)
export const useInventory = (outletId?: string) => {
  return useQuery({
    queryKey: ['inventory', outletId],
    queryFn: async (): Promise<InventoryItem[]> => {
      const params = outletId ? { outlet_id: outletId, limit: 1000 } : { limit: 1000 };
      const { data } = await apiClient.get<any>('/inventory/', { params });
      return data.items || [];
    },
  });
};

// Adjust stock levels
export const useAdjustStock = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, quantity_added }: { id: string; quantity_added: number }) => {
      const { data } = await apiClient.patch(`/inventory/${id}/stock`, { quantity_added });
      return data;
    },
    onSuccess: () => {
      // Refresh inventory data globally after a successful stock update
      queryClient.invalidateQueries({ queryKey:['inventory'] });
    },
  });
};