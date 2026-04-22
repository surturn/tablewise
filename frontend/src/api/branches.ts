import {apiClient} from './client';

export interface Branch {
  id: string;
  name: string;
  location: string;
  contact_number: string;
  is_active: boolean;
  opening_time: string;
  closing_time: string;
}

export const fetchBranches = async (): Promise<Branch[]> => {
  const response = await apiClient.get<Branch[]>('/branches/');
  return response.data;
};