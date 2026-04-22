import {apiClient} from './client';

export interface Customer {
  id: string;
  phone_number: string;
  full_name: string;
  email: string | null;
  loyalty_points: number;
}

export const fetchCustomers = async (): Promise<Customer[]> => {
  const response = await apiClient.get<Customer[]>('/customers');
  return response.data;
};