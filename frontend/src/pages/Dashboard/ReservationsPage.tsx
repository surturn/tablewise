import React from 'react';
import { m } from 'framer-motion';
import { useBookings, useUpdateBookingStatus } from '../../api/bookings';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { SkeletonTable } from '../../components/ui/Skeleton';
import { CalendarCheck } from 'lucide-react';
import { useToastStore } from '../../store/toastStore';

const ReservationsPage: React.FC = () => {
  const { data, isLoading } = useBookings();
  const updateStatus = useUpdateBookingStatus();
  const addToast = useToastStore(s => s.addToast);

  const bookings = data?.items || [];

  const handleStatusChange = (bookingId: string, newStatus: string) => {
    updateStatus.mutate({ bookingId, status: newStatus }, {
      onSuccess: () => addToast('Booking status updated', 'success'),
      onError: () => addToast('Failed to update booking status', 'error')
    });
  };

  if (isLoading) return <SkeletonTable rows={10} />;

  return (
    <m.div className="bg-white rounded-2xl border border-stone-200 shadow-subtle overflow-hidden">
      <div className="px-6 py-5 border-b border-stone-200 flex items-center justify-between">
        <h2 className="text-xl font-bold text-brand-dark flex items-center gap-2">
          <CalendarCheck className="text-brand-orange" /> Bookings & Reservations
        </h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-stone-600">
          <thead className="bg-stone-50 border-b border-stone-200">
            <tr>
              <th className="px-6 py-4 font-bold text-brand-dark">Guest</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Room</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Dates</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Total</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Status</th>
              <th className="px-6 py-4 font-bold text-brand-dark text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {bookings.map((booking) => (
              <tr key={booking.id} className="hover:bg-stone-50 transition-colors">
                <td className="px-6 py-4 font-medium text-brand-dark">{booking.guest?.full_name || booking.guest_id.substring(0,8)}</td>
                <td className="px-6 py-4">{booking.room?.room_number || booking.room_id.substring(0,8)}</td>
                <td className="px-6 py-4 text-xs text-stone-500">
                  {new Date(booking.check_in).toLocaleDateString()} - {new Date(booking.check_out).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 font-medium">${(booking.total_usd_cents / 100).toFixed(2)}</td>
                <td className="px-6 py-4">
                  <StatusBadge status={booking.status} />
                  <div className="mt-1"><StatusBadge status={booking.payment_status} /></div>
                </td>
                <td className="px-6 py-4 text-right">
                  <select 
                    value={booking.status}
                    onChange={(e) => handleStatusChange(booking.id, e.target.value)}
                    className="border border-stone-200 rounded-lg text-sm p-2 outline-none focus:ring-2 focus:ring-brand-orange"
                    disabled={updateStatus.isPending}
                  >
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="checked_in">Checked In</option>
                    <option value="checked_out">Checked Out</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </m.div>
  );
};

export default ReservationsPage;
