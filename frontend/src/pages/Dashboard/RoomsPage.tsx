import React from 'react';
import { m } from 'framer-motion';
import { useRooms, useUpdateRoomStatus } from '../../api/rooms';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { SkeletonTable } from '../../components/ui/Skeleton';
import { BedDouble } from 'lucide-react';
import { useToastStore } from '../../store/toastStore';

const RoomsPage: React.FC = () => {
  const { data: rooms, isLoading } = useRooms();
  const updateStatus = useUpdateRoomStatus();
  const addToast = useToastStore(s => s.addToast);

  const handleStatusChange = (roomId: string, newStatus: string) => {
    updateStatus.mutate({ roomId, status: newStatus }, {
      onSuccess: () => addToast('Room status updated', 'success'),
      onError: () => addToast('Failed to update room status', 'error')
    });
  };

  if (isLoading) return <SkeletonTable rows={10} />;

  return (
    <m.div className="bg-white rounded-2xl border border-stone-200 shadow-subtle overflow-hidden">
      <div className="px-6 py-5 border-b border-stone-200 flex items-center justify-between">
        <h2 className="text-xl font-bold text-brand-dark flex items-center gap-2">
          <BedDouble className="text-brand-orange" /> Room Management
        </h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-stone-600">
          <thead className="bg-stone-50 border-b border-stone-200">
            <tr>
              <th className="px-6 py-4 font-bold text-brand-dark">Room No.</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Floor</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Type</th>
              <th className="px-6 py-4 font-bold text-brand-dark">Status</th>
              <th className="px-6 py-4 font-bold text-brand-dark text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {rooms?.map((room) => (
              <tr key={room.id} className="hover:bg-stone-50 transition-colors">
                <td className="px-6 py-4 font-bold text-brand-dark">{room.room_number}</td>
                <td className="px-6 py-4">{room.floor}</td>
                <td className="px-6 py-4 text-stone-500">{room.room_type_id.substring(0, 8)}</td>
                <td className="px-6 py-4">
                  <StatusBadge status={room.status} />
                </td>
                <td className="px-6 py-4 text-right">
                  <select 
                    value={room.status}
                    onChange={(e) => handleStatusChange(room.id, e.target.value)}
                    className="border border-stone-200 rounded-lg text-sm p-2 outline-none focus:ring-2 focus:ring-brand-orange"
                    disabled={updateStatus.isPending}
                  >
                    <option value="available">Available</option>
                    <option value="occupied">Occupied</option>
                    <option value="cleaning">Cleaning</option>
                    <option value="maintenance">Maintenance</option>
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

export default RoomsPage;
