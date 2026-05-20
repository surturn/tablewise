import React, { useState } from 'react';
import { m } from 'framer-motion';
import { useRoomTypes } from '../../api/rooms';
import { useCreateBooking } from '../../api/bookings';
import { useToastStore } from '../../store/toastStore';
import Navbar from '../../components/Layout/Navbar';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { Modal } from '../../components/ui/Modal';
import { Users, Info } from 'lucide-react';

const Book: React.FC = () => {
  const { data: roomTypes = [], isLoading } = useRoomTypes();
  const createBooking = useCreateBooking();
  const addToast = useToastStore((state) => state.addToast);
  
  const [dates, setDates] = useState({ check_in: '', check_out: '' });
  const [selectedRoomTypeId, setSelectedRoomTypeId] = useState<string | null>(null);
  const [guest, setGuest] = useState({ full_name: '', phone_number: '', email: '' });

  const handleBook = () => {
    if (!selectedRoomTypeId) return;
    createBooking.mutate({
      room_type_id: selectedRoomTypeId,
      guest: {
        full_name: guest.full_name,
        phone_number: guest.phone_number,
        email: guest.email
      },
      check_in: dates.check_in,
      check_out: dates.check_out,
      extras: []
    }, {
      onSuccess: () => {
        addToast('Booking created successfully! Redirecting to payment...', 'success');
        setSelectedRoomTypeId(null);
        setGuest({ full_name: '', phone_number: '', email: '' });
      },
      onError: (err: any) => {
        addToast(err.response?.data?.detail || 'Failed to create booking.', 'error');
      }
    });
  };

  return (
    <div className="min-h-screen bg-brand-light">
      <Navbar />
      <main className="mx-auto max-w-5xl p-6 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-black text-brand-dark mb-4">Book your stay</h1>
          <p className="text-stone-500 text-lg">Experience luxury and comfort in Juba.</p>
        </div>
        
        <section className="bg-white p-6 rounded-2xl shadow-subtle border border-stone-100 mb-8 grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Check-in Date</label>
            <input className="w-full rounded-lg border border-stone-200 p-3 focus:ring-2 focus:ring-brand-orange outline-none" type="date" value={dates.check_in} onChange={e => setDates({ ...dates, check_in: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Check-out Date</label>
            <input className="w-full rounded-lg border border-stone-200 p-3 focus:ring-2 focus:ring-brand-orange outline-none" type="date" value={dates.check_out} onChange={e => setDates({ ...dates, check_out: e.target.value })} />
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          {isLoading && Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
          
          {!isLoading && roomTypes.map((rt, i) => (
            <m.article 
              key={rt.id} 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="rounded-2xl border border-stone-200 bg-white overflow-hidden flex flex-col shadow-subtle"
            >
              {rt.photos?.[0] ? (
                <img src={rt.photos[0]} alt={rt.name} className="h-48 w-full object-cover" />
              ) : (
                <div className="h-48 w-full bg-stone-100 flex items-center justify-center text-stone-300">
                  <Info size={32} />
                </div>
              )}
              <div className="p-5 flex flex-col flex-1">
                <h2 className="text-xl font-bold text-brand-dark mb-2">{rt.name}</h2>
                <p className="text-sm text-stone-500 mb-4 line-clamp-2 flex-1">{rt.description}</p>
                
                <div className="flex items-center gap-2 text-sm text-stone-600 mb-4 bg-stone-50 p-2 rounded-lg">
                  <Users size={16} className="text-brand-orange" />
                  <span>Up to {rt.capacity} guests</span>
                </div>
                
                <div className="flex justify-between items-end mt-auto pt-4 border-t border-stone-100">
                  <div>
                    <span className="text-2xl font-black text-brand-dark">${(rt.base_price_usd_cents / 100).toFixed(2)}</span>
                    <span className="text-stone-500 text-sm"> / night</span>
                  </div>
                  <button 
                    onClick={() => {
                      if (!dates.check_in || !dates.check_out) {
                        addToast('Please select dates first', 'warning');
                        return;
                      }
                      setSelectedRoomTypeId(rt.id);
                    }}
                    className="rounded-full bg-brand-dark px-5 py-2 text-white font-medium hover:bg-brand-orange transition-colors"
                  >
                    Select
                  </button>
                </div>
              </div>
            </m.article>
          ))}
        </section>

        <Modal 
          isOpen={!!selectedRoomTypeId} 
          onClose={() => setSelectedRoomTypeId(null)}
          title="Guest Details"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Full Name</label>
              <input type="text" value={guest.full_name} onChange={e => setGuest({...guest, full_name: e.target.value})} className="w-full rounded-lg border border-stone-200 p-3 focus:ring-2 focus:ring-brand-orange outline-none" placeholder="John Doe" />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Phone Number</label>
              <input type="tel" value={guest.phone_number} onChange={e => setGuest({...guest, phone_number: e.target.value})} className="w-full rounded-lg border border-stone-200 p-3 focus:ring-2 focus:ring-brand-orange outline-none" placeholder="+211..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Email</label>
              <input type="email" value={guest.email} onChange={e => setGuest({...guest, email: e.target.value})} className="w-full rounded-lg border border-stone-200 p-3 focus:ring-2 focus:ring-brand-orange outline-none" placeholder="john@example.com" />
            </div>
            <button 
              onClick={handleBook}
              disabled={createBooking.isPending || !guest.full_name || !guest.phone_number}
              className="w-full mt-4 bg-brand-dark text-white rounded-lg py-3 font-bold hover:bg-brand-orange transition-colors disabled:opacity-50"
            >
              {createBooking.isPending ? 'Processing...' : 'Confirm Booking'}
            </button>
          </div>
        </Modal>
      </main>
    </div>
  );
};
export default Book;
