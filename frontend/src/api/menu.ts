import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface MenuItem {
  id: string;
  outlet_id: string;
  name: string;
  description: string;
  price_usd_cents: number;
  image_url: string | null;
  category_id: string;
}

export const useMenuItems = (outletId?: string, categoryId?: string) => {
  return useQuery({
    queryKey: ['menuItems', outletId, categoryId],
    queryFn: async (): Promise<MenuItem[]> => {
      const params = { outlet_id: outletId, ...(categoryId ? { category_id: categoryId } : {}) };
      const { data } = await apiClient.get('/menu/items', { params });
      return data;
    },
    enabled: Boolean(outletId),
  });
};
