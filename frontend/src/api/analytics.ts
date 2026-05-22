import {apiClient} from './client';

export interface ForecastRequest {
  branch_id: string;
  historical_data_summary: string;
}

export interface ForecastResponse {
  task_id: string;
  message: string;
}

export const requestForecast = async (data: ForecastRequest): Promise<ForecastResponse> => {
  const response = await apiClient.post<ForecastResponse>('/analytics/forecast', data);
  return response.data;
};

export const fetchAnalyticsOverview = async (outletId?: string) => {
  const params = outletId ? { outlet_id: outletId } : {};
  const { data } = await apiClient.get('/analytics/overview', { params });
  return data;
};