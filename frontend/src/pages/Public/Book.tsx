import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

interface RoomType { id: string; name: string; description: string; capacity: number; base_price_usd_cents: number; amenities: string[]; photos: string[]; available_count: number }

const Book: React.FC = () => {
  const [dates, setDates] = useState({ check_in: '', check_out: '' });
  const { data = [] } = useQuery({ queryKey: ['room-types'], queryFn: async () => (await apiClient.get<RoomType[]>('/room-types/')).data });
  return <main className="mx-auto max-w-5xl p-6"><h1 className="text-3xl font-bold">Book your stay at Grand Hotel Juba</h1><section className="my-6 grid gap-4 md:grid-cols-2"><input className="rounded border p-3" type="date" value={dates.check_in} onChange={e => setDates({ ...dates, check_in: e.target.value })} /><input className="rounded border p-3" type="date" value={dates.check_out} onChange={e => setDates({ ...dates, check_out: e.target.value })} /></section><section className="grid gap-4 md:grid-cols-3">{data.map(rt => <article key={rt.id} className="rounded-xl border p-4 shadow-sm"><h2 className="text-xl font-semibold">{rt.name}</h2><p className="text-sm text-gray-600">{rt.description}</p><p className="mt-2">Capacity: {rt.capacity}</p><p className="font-bold">${(rt.base_price_usd_cents / 100).toFixed(2)} / night</p><p className="text-sm text-green-700">{rt.available_count} available</p><button className="mt-4 rounded bg-[#121212] px-4 py-2 text-white">Continue to guest details & Stripe payment</button></article>)}</section></main>;
};
export default Book;
