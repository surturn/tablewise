import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface Room { id: string; room_number: string; floor: number; status: string; room_type_id: string }
const colors: Record<string, string> = { available: 'bg-green-100 text-green-800', occupied: 'bg-red-100 text-red-800', cleaning: 'bg-yellow-100 text-yellow-800', maintenance: 'bg-gray-200 text-gray-800' };

const RoomsPage: React.FC = () => {
  const { data = [] } = useQuery({ queryKey: ['rooms'], queryFn: async () => (await apiClient.get<Room[]>('/rooms/')).data });
  return <div className="p-6"><h1 className="text-2xl font-bold mb-4">Room Status Board</h1><div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-4">{data.map(room => <button key={room.id} className="rounded-xl border p-4 text-left shadow-sm hover:shadow-md"><div className="text-xl font-semibold">Room {room.room_number}</div><div className="text-sm text-gray-500">Floor {room.floor}</div><span className={`mt-4 inline-block rounded-full px-3 py-1 text-sm ${colors[room.status]}`}>{room.status}</span></button>)}</div></div>;
};
export default RoomsPage;
