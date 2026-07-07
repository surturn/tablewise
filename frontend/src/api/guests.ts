import { apiClient } from './client';

export interface Guest {
  id: string;
  phone_number: string;
  full_name: string;
  email: string | null;
  nationality?: string;
  loyalty_points: number;
  total_spend_kes_cents: number;
}

export const fetchGuests = async (): Promise<Guest[]> => {
  const response = await apiClient.get<any>('/guests/', { params: { limit: 1000 } });
  return response.data.items || response.data;
};
