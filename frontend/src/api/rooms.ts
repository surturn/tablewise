import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface RoomType {
  id: string;
  property_id: string;
  name: string;
  description: string;
  capacity: number;
  base_price_kes_cents: number;
  amenities: string[];
  photos: string[];
}

export interface Room {
  id: string;
  room_type_id: string;
  room_number: string;
  floor: number;
  status: 'available' | 'occupied' | 'cleaning' | 'maintenance';
}

export const useRoomTypes = () => {
  return useQuery({
    queryKey: ['roomTypes'],
    queryFn: async (): Promise<RoomType[]> => {
      const { data } = await apiClient.get('/room-types/');
      return data;
    },
  });
};

export const useRooms = (status?: string) => {
  return useQuery({
    queryKey: ['rooms', status],
    queryFn: async (): Promise<Room[]> => {
      const params = status ? { status } : {};
      const { data } = await apiClient.get('/rooms/', { params });
      return data.items || data;
    },
  });
};

export const useUpdateRoomStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ roomId, status }: { roomId: string; status: string }) => {
      const { data } = await apiClient.patch(`/rooms/${roomId}/status`, { status });
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rooms'] }),
  });
};
