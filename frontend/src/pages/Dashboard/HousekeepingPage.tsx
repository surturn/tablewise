import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface Room { id: string; room_number: string; floor: number; status: string }

const HousekeepingPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { data = [] } = useQuery({ queryKey: ['rooms', 'cleaning'], queryFn: async () => (await apiClient.get<Room[]>('/rooms/', { params: { status: 'cleaning' } })).data });
  const markAvailable = useMutation({ mutationFn: (roomId: string) => apiClient.put(`/rooms/${roomId}/status`, { status: 'available' }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rooms'] }) });
  return <div className="p-6"><h1 className="text-2xl font-bold mb-4">Housekeeping</h1><div className="space-y-3">{data.map(room => <div key={room.id} className="flex items-center justify-between rounded-lg border p-4"><span>Room {room.room_number} · Floor {room.floor}</span><button className="rounded bg-green-700 px-3 py-2 text-white" onClick={() => markAvailable.mutate(room.id)}>Mark available</button></div>)}</div></div>;
};
export default HousekeepingPage;
