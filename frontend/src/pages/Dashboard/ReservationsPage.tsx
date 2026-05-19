import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface Booking { id: string; room_id: string; check_in: string; check_out: string; status: string; total_usd_cents: number }
const color: Record<string, string> = { pending: 'bg-blue-500', confirmed: 'bg-green-500', checked_in: 'bg-teal-500', checked_out: 'bg-gray-500', cancelled: 'bg-red-500' };

const ReservationsPage: React.FC = () => {
  const { data } = useQuery({ queryKey: ['bookings'], queryFn: async () => (await apiClient.get('/bookings/')).data });
  const bookings: Booking[] = data?.items ?? [];
  return <div className="p-6"><h1 className="text-2xl font-bold mb-4">Reservation Calendar</h1><div className="space-y-3">{bookings.map(b => <div key={b.id} className="rounded-lg border bg-white p-4"><div className={`h-2 rounded ${color[b.status]} mb-3`} /><div className="font-semibold">Booking {b.id.slice(0, 8)}</div><div className="text-sm text-gray-600">{b.check_in} → {b.check_out} · ${(b.total_usd_cents / 100).toFixed(2)}</div></div>)}</div></div>;
};
export default ReservationsPage;
