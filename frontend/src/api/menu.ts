import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string | null;
  category_id: string;
}

// React Query hook to fetch menu items
export const useMenuItems = (categoryId?: string) => {
  return useQuery({
    queryKey: ['menuItems', categoryId],
    queryFn: async (): Promise<MenuItem[]> => {
      const params = categoryId ? { category_id: categoryId } : {};
      const { data } = await apiClient.get('/menu/items', { params });
      return data;
    },
  });
};