import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface BookingGuest {
  phone_number: string;
  full_name: string;
  email?: string;
  nationality?: string;
}

export interface BookingExtra {
  name: string;
  price_kes_cents: number;
}

export interface Booking {
  id: string;
  room_id: string;
  guest_id: string;
  check_in: string;
  check_out: string;
  status: 'pending' | 'confirmed' | 'checked_in' | 'checked_out' | 'cancelled';
  total_kes_cents: number;
  payment_status: 'unpaid' | 'partial' | 'paid' | 'failed' | 'refunded';
  notes?: string;
  extras: BookingExtra[];
  room?: any;
  guest?: any;
}

export interface PaginatedBookings {
  items: Booking[];
  total: number;
  page: number;
  pages: number;
}

export const useBookings = (params?: { page?: number; limit?: number; status?: string; dateFrom?: string; dateTo?: string }) => {
  return useQuery({
    queryKey: ['bookings', params],
    queryFn: async (): Promise<PaginatedBookings> => {
      const { data } = await apiClient.get('/bookings/', { params });
      return data;
    },
  });
};

export const useCreateBooking = () => {
  return useMutation({
    mutationFn: async (payload: { room_type_id: string; guest: BookingGuest; check_in: string; check_out: string; extras: BookingExtra[]; notes?: string }) => {
      const { data } = await apiClient.post('/bookings/', payload);
      return data;
    },
  });
};

export const useUpdateBookingStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ bookingId, status }: { bookingId: string; status: string }) => {
      const { data } = await apiClient.put(`/bookings/${bookingId}/status`, { status });
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookings'] }),
  });
};
