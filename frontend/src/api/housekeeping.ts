import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export const useScheduleHousekeeping = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (roomId: string) => {
      const { data } = await apiClient.post(`/rooms/${roomId}/housekeeping/schedule`);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rooms'] }),
  });
};
