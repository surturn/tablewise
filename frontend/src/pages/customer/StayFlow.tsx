import React, { useEffect, useState } from 'react';
import { m } from 'framer-motion';
import { Calendar, Users, ChevronLeft, CheckCircle2 } from 'lucide-react';
import CustomerNavbar from '../../components/customer/CustomerNavbar';
import RoomTypeCard from '../../components/customer/RoomTypeCard';
import { SkeletonCard } from '../../components/ui/Skeleton';
import { AnimatedPage, springs } from '../../components/ui/MotionConfig';
import { apiClient as client } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { format, addDays } from 'date-fns';

const StayFlow: React.FC = () => {
  const { user } = useAuth();
  const [roomTypes, setRoomTypes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Booking Form State
  const [selectedRoom, setSelectedRoom] = useState<any | null>(null);
  const [checkIn, setCheckIn] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [checkOut, setCheckOut] = useState(format(addDays(new Date(), 1), 'yyyy-MM-dd'));
  const [guestsCount, setGuestsCount] = useState('1');
  const [isBooking, setIsBooking] = useState(false);
  const [bookingConfirmed, setBookingConfirmed] = useState<any>(null);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        setIsLoading(true);
        const res = await client.get('/api/v1/room-types/');
        setRoomTypes(res.data);
      } catch (err) {
        console.error("Failed to load rooms", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRooms();
  }, []);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoom || !user) return;
    
    setIsBooking(true);
    try {
      const payload = {
        room_type_id: selectedRoom.id,
        guest: {
          full_name: user.full_name,
          email: user.email,
          phone_number: user.phone_number || '000000000',
        },
        check_in: checkIn,
        check_out: checkOut,
        extras: [],
        notes: ''
      };
      const res = await client.post('/api/v1/bookings/', payload);
      setBookingConfirmed(res.data);
      setSelectedRoom(null);
    } catch (err) {
      console.error("Failed to book room", err);
    } finally {
      setIsBooking(false);
    }
  };

  if (bookingConfirmed) {
    return (
      <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
        <CustomerNavbar />
        <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-12 flex flex-col items-center justify-center">
          <m.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={springs.snappy}
            className="bg-white p-8 rounded-3xl shadow-card text-center w-full"
          >
            <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} className="text-green-500" />
            </div>
            <h2 className="text-3xl font-black text-stone-900 mb-2">Booking Confirmed!</h2>
            <p className="text-stone-500 mb-8">We can't wait to host you.</p>
            
            <div className="bg-stone-50 rounded-2xl p-6 mb-8 text-left border border-stone-100">
              <p className="text-xs font-bold text-stone-400 uppercase tracking-wider mb-4">Reservation Details</p>
              <div className="space-y-3 font-medium text-stone-800">
                <div className="flex justify-between border-b border-stone-200 pb-2">
                  <span className="text-stone-500">Check-in:</span>
                  <span>{bookingConfirmed.check_in}</span>
                </div>
                <div className="flex justify-between border-b border-stone-200 pb-2">
                  <span className="text-stone-500">Check-out:</span>
                  <span>{bookingConfirmed.check_out}</span>
                </div>
                <div className="flex justify-between pb-2">
                  <span className="text-stone-500">Reference:</span>
                  <span className="font-mono">{bookingConfirmed.id.split('-')[0].toUpperCase()}</span>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setBookingConfirmed(null)}
              className="w-full py-4 bg-brand-orange text-brand-dark font-bold rounded-xl hover:bg-amber-400 transition-colors shadow-sm"
            >
              Done
            </button>
          </m.div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
      <CustomerNavbar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12 relative">
        <AnimatedPage>
          {!selectedRoom ? (
            <>
              <div className="mb-10 text-center">
                <h1 className="text-4xl font-black text-brand-dark mb-4">Find your stay</h1>
                <p className="text-stone-500 font-medium text-lg max-w-2xl mx-auto">Experience comfort and luxury tailored to your preferences.</p>
              </div>

              <div className="space-y-6">
                {isLoading ? (
                  [1, 2, 3].map(i => <div key={i}><SkeletonCard /></div>)
                ) : (
                  roomTypes.map((room, i) => (
                    <RoomTypeCard
                      key={room.id}
                      id={room.id}
                      name={room.name}
                      description={room.description}
                      capacity={room.capacity}
                      basePriceUsdCents={room.base_price_usd_cents}
                      availableCount={room.available_count}
                      amenities={room.amenities}
                      photos={room.photos}
                      onSelect={() => setSelectedRoom(room)}
                      delay={i * 0.1}
                    />
                  ))
                )}
              </div>
            </>
          ) : (
            <m.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={springs.smooth}
              className="max-w-xl mx-auto bg-white p-8 rounded-3xl shadow-elevated border border-stone-100"
            >
              <button 
                onClick={() => setSelectedRoom(null)} 
                className="flex items-center gap-2 text-stone-500 hover:text-brand-orange font-medium mb-8 transition-colors"
              >
                <ChevronLeft size={20} /> Back to Rooms
              </button>
              
              <div className="mb-8 pb-8 border-b border-stone-100">
                <h2 className="text-2xl font-black text-stone-900 mb-2">Book {selectedRoom.name}</h2>
                <p className="text-stone-500 font-medium">${(selectedRoom.base_price_usd_cents / 100).toFixed(2)} per night</p>
              </div>

              <form onSubmit={handleBook} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-stone-700 mb-2">Check-in</label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-3 text-stone-400" size={18} />
                      <input
                        type="date"
                        required
                        value={checkIn}
                        onChange={e => setCheckIn(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all font-medium text-stone-700"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-stone-700 mb-2">Check-out</label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-3 text-stone-400" size={18} />
                      <input
                        type="date"
                        required
                        value={checkOut}
                        onChange={e => setCheckOut(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all font-medium text-stone-700"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-stone-700 mb-2">Number of Guests</label>
                  <div className="relative">
                    <Users className="absolute left-3 top-3 text-stone-400" size={18} />
                    <select
                      value={guestsCount}
                      onChange={e => setGuestsCount(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-orange/50 transition-all font-medium text-stone-700 appearance-none"
                    >
                      {[...Array(selectedRoom.capacity)].map((_, i) => (
                        <option key={i+1} value={i+1}>{i+1} {i === 0 ? 'Guest' : 'Guests'}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="pt-6">
                  <button
                    type="submit"
                    disabled={isBooking}
                    className="w-full py-4 bg-brand-dark text-white font-bold rounded-xl hover:bg-black transition-colors shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {isBooking ? 'Confirming...' : 'Confirm Reservation'}
                  </button>
                </div>
              </form>
            </m.div>
          )}
        </AnimatedPage>
      </main>
    </div>
  );
};

export default StayFlow;
