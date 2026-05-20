import React from 'react';
import { m } from 'framer-motion';
import { useRooms } from '../../api/rooms';
import { useScheduleHousekeeping } from '../../api/housekeeping';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { SkeletonTable } from '../../components/ui/Skeleton';
import { SprayCan, CheckCircle } from 'lucide-react';
import { useToastStore } from '../../store/toastStore';

const HousekeepingPage: React.FC = () => {
  const { data: rooms, isLoading } = useRooms();
  const scheduleHousekeeping = useScheduleHousekeeping();
  const addToast = useToastStore(s => s.addToast);

  const handleSchedule = (roomId: string) => {
    scheduleHousekeeping.mutate(roomId, {
      onSuccess: () => addToast('Housekeeping scheduled successfully', 'success'),
      onError: () => addToast('Failed to schedule housekeeping', 'error')
    });
  };

  if (isLoading) return <SkeletonTable rows={10} />;

  // Filter only rooms that are occupied or need cleaning
  const priorityRooms = rooms?.filter(r => ['cleaning', 'occupied'].includes(r.status)) || [];

  return (
    <m.div className="bg-white rounded-2xl border border-stone-200 shadow-subtle overflow-hidden">
      <div className="px-6 py-5 border-b border-stone-200 flex items-center justify-between">
        <h2 className="text-xl font-bold text-brand-dark flex items-center gap-2">
          <SprayCan className="text-brand-orange" /> Housekeeping Schedule
        </h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-stone-600">
          <thead className="bg-stone-50 border-b border-stone-200">
            <tr>
              <th className="px-6 py-4 font-bold text-brand-dark">Room No.</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Floor</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Status</th>
              <th className="px-6 py-4 font-bold text-brand-dark text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {priorityRooms.map((room) => (
              <tr key={room.id} className="hover:bg-stone-50 transition-colors">
                <td className="px-6 py-4 font-bold text-brand-dark">{room.room_number}</td>
                <td className="px-6 py-4">{room.floor}</td>
                <td className="px-6 py-4">
                  <StatusBadge status={room.status} />
                </td>
                <td className="px-6 py-4 text-right">
                  <button 
                    onClick={() => handleSchedule(room.id)}
                    disabled={scheduleHousekeeping.isPending}
                    className="inline-flex items-center gap-2 bg-stone-100 hover:bg-stone-200 text-stone-700 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                  >
                    <CheckCircle size={16} /> Mark Cleaned
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {priorityRooms.length === 0 && (
        <div className="p-12 text-center text-stone-500">
          All rooms are clean!
        </div>
      )}
    </m.div>
  );
};

export default HousekeepingPage;
