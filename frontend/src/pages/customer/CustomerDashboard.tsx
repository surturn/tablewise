import React, { useEffect, useState } from 'react';
import { ShoppingBag, Calendar, Coffee } from 'lucide-react';
import CustomerNavbar from '../../components/customer/CustomerNavbar';
import { StatCard } from '../../components/ui/StatCard';
import { AnimatedPage, FadeIn } from '../../components/ui/MotionConfig';
import { apiClient as client } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { StatusBadge } from '../../components/ui/StatusBadge';

const CustomerDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeOrders, setActiveOrders] = useState<any[]>([]);
  const [activeBookings, setActiveBookings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        // Note: the backend requires outlet_id for orders, if we don't have it we might just fetch the first page 
        // For dashboard purposes, we simulate fetching user's recent active data 
        // In a real scenario with proper customer endpoints we would fetch exactly by guest_id.
        const [ordersRes, bookingsRes] = await Promise.all([
          client.get('/api/v1/orders/'),
          client.get('/api/v1/bookings/')
        ]);
        
        // Filter for active items belonging to this user
        // (Assuming backend doesn't filter by guest_id by default since we hit staff endpoints to stub)
        const userOrders = ordersRes.data.items?.filter((o: any) => o.guest_id === user?.id && ['created', 'pending', 'preparing', 'ready', 'dispatched'].includes(o.status)) || [];
        const userBookings = bookingsRes.data.items?.filter((b: any) => b.guest_id === user?.id && ['confirmed', 'checked_in'].includes(b.status)) || [];
        
        setActiveOrders(userOrders);
        setActiveBookings(userBookings);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  return (
    <div className="min-h-screen bg-brand-light font-sans text-brand-dark flex flex-col">
      <CustomerNavbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
        <AnimatedPage>
          <div className="mb-10">
            <h1 className="text-3xl font-black text-brand-dark mb-2">Welcome back, {user?.full_name?.split(' ')[0]}</h1>
            <p className="text-stone-500 font-medium">Here's what's happening with your stay.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <StatCard 
              title="Active Food Orders"
              value={activeOrders.filter(o => o.order_type !== 'dine_in').length.toString()}
              icon={<ShoppingBag size={24} />}
              delay={0.1}
            />
            <StatCard 
              title="Current Stays"
              value={activeBookings.length.toString()}
              icon={<Calendar size={24} />}
              delay={0.2}
            />
            <StatCard 
              title="Open Bar Tabs"
              value={activeOrders.filter(o => o.order_type === 'dine_in').length.toString()}
              icon={<Coffee size={24} />}
              delay={0.3}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <FadeIn delay={0.4}>
              <div className="bg-white rounded-3xl p-8 border border-stone-100 shadow-subtle">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-stone-900">Recent Activity</h2>
                  <span className="text-sm font-medium text-brand-orange cursor-pointer hover:underline">View All</span>
                </div>
                
                {isLoading ? (
                  <div className="space-y-4 animate-pulse">
                    {[1, 2, 3].map(i => (
                      <div key={i} className="h-16 bg-stone-100 rounded-xl"></div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {activeOrders.length === 0 && activeBookings.length === 0 ? (
                      <div className="text-center py-8">
                        <p className="text-stone-500">No active orders or bookings right now.</p>
                      </div>
                    ) : (
                      <>
                        {activeOrders.slice(0, 3).map((order: any) => (
                          <div key={order.id} className="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100">
                            <div className="flex items-center gap-4">
                              <div className="p-2.5 bg-white rounded-lg text-brand-orange shadow-sm">
                                {order.order_type === 'dine_in' ? <Coffee size={18} /> : <ShoppingBag size={18} />}
                              </div>
                              <div>
                                <p className="font-bold text-sm text-stone-900">{order.order_type === 'dine_in' ? 'Bar Tab' : 'Food Order'}</p>
                                <p className="text-xs text-stone-500">${(order.total_usd_cents / 100).toFixed(2)}</p>
                              </div>
                            </div>
                            <StatusBadge status={order.status} />
                          </div>
                        ))}
                        {activeBookings.slice(0, 3).map((booking: any) => (
                          <div key={booking.id} className="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100">
                            <div className="flex items-center gap-4">
                              <div className="p-2.5 bg-white rounded-lg text-brand-orange shadow-sm">
                                <Calendar size={18} />
                              </div>
                              <div>
                                <p className="font-bold text-sm text-stone-900">Room Booking</p>
                                <p className="text-xs text-stone-500">In {booking.check_in}</p>
                              </div>
                            </div>
                            <StatusBadge status={booking.status} />
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                )}
              </div>
            </FadeIn>
            
            <FadeIn delay={0.5}>
              <div className="bg-stone-900 rounded-3xl p-8 text-white shadow-elevated relative overflow-hidden">
                <div className="absolute -top-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-brand-orange/20 blur-[60px] pointer-events-none" />
                <h2 className="text-2xl font-black mb-2 relative z-10">Grand Platform Rewards</h2>
                <p className="text-stone-400 mb-8 relative z-10">Earn points on every order and booking.</p>
                
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10 mb-6 relative z-10">
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-stone-300 font-medium">Available Points</span>
                    <span className="text-3xl font-black text-brand-orange">1,250</span>
                  </div>
                  <div className="w-full bg-stone-800 rounded-full h-2 mt-4">
                    <div className="bg-brand-orange h-2 rounded-full" style={{ width: '65%' }}></div>
                  </div>
                  <p className="text-xs text-stone-400 mt-2 text-right">750 points to Gold Tier</p>
                </div>
                
                <button className="w-full py-3 bg-brand-orange text-brand-dark font-bold rounded-xl hover:bg-amber-400 transition-colors relative z-10 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
                  Redeem Rewards
                </button>
              </div>
            </FadeIn>
          </div>
        </AnimatedPage>
      </main>
    </div>
  );
};

export default CustomerDashboard;
