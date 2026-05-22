import { apiClient } from './client';

export interface Outlet {
  id: string;
  name: string;
  location: string;
  contact_number: string;
  is_active: boolean;
  opening_time: string;
  closing_time: string;
  type: 'restaurant' | 'bar';
}

export const fetchOutlets = async (): Promise<Outlet[]> => {
  const response = await apiClient.get<any>('/outlets/');
  return response.data.items || response.data;
};
